import streamlit as st
import pandas as pd
from datetime import datetime
import db
from pdf_generator import InvoicePDF
import os

# Initialize the database
db.init_db()

st.set_page_config(layout="wide", page_title="Glanzwerk Rheinland Invoicing")

st.title("Glanzwerk Rheinland - Rechnungssystem")

# --- Main App ---

menu = ["Neue Rechnung", "Services verwalten", "Kundenhistorie"]
choice = st.sidebar.selectbox("Menü", menu)

if choice == "Neue Rechnung":
    st.subheader("Neue Rechnung erstellen")

    # Customer Details
    with st.expander("Kundendetails", expanded=True):
        customer_name = st.text_input("Kundenname")
        kfz = st.text_input("KFZ-Kennzeichen")
        tel = st.text_input("Telefon (optional)")

    # Invoice Items
    st.subheader("Rechnungspositionen")

    if "invoice_items" not in st.session_state:
        st.session_state.invoice_items = []

    services = db.get_all_services()
    service_names = [s["name"] for s in services]

    col1, col2 = st.columns(2)
    with col1:
        selected_service = st.selectbox("Service auswählen", [""] + service_names)
    with col2:
        if st.button("Service hinzufügen") and selected_service:
            service_details = db.get_service_by_name(selected_service)
            st.session_state.invoice_items.append({
                "service_name": service_details["name"],
                "qty": 1,
                "unit_price": service_details["standard_price"],
                "line_total": service_details["standard_price"]
            })

    with st.expander("Individuellen Service hinzufügen"):
        custom_service_name = st.text_input("Servicename")
        custom_service_price = st.number_input("Preis", min_value=0.0, step=0.50)
        if st.button("Individuellen Service hinzufügen") and custom_service_name and custom_service_price > 0:
            st.session_state.invoice_items.append({
                "service_name": custom_service_name,
                "qty": 1,
                "unit_price": custom_service_price,
                "line_total": custom_service_price
            })

    if st.session_state.invoice_items:
        items_df = pd.DataFrame(st.session_state.invoice_items)
        st.write(items_df)

        for i, item in enumerate(st.session_state.invoice_items):
            service_name = item["service_name"]
            st.session_state.invoice_items[i]["qty"] = st.number_input(f"Anzahl für {service_name}", min_value=1, value=item["qty"], key=f"qty_{i}")
            st.session_state.invoice_items[i]["unit_price"] = st.number_input(f"Einzelpreis für {service_name}", min_value=0.0, value=item["unit_price"], key=f"price_{i}")
            st.session_state.invoice_items[i]["line_total"] = st.session_state.invoice_items[i]["qty"] * st.session_state.invoice_items[i]["unit_price"]
            if st.button(f"Entfernen", key=f"remove_{i}"):
                st.session_state.invoice_items.pop(i)
                st.experimental_rerun()

    # Summary
    st.subheader("Zusammenfassung")
    subtotal = sum(item["line_total"] for item in st.session_state.invoice_items)
    discount = st.number_input("Rabatt (fester Betrag)", min_value=0.0, step=5.0)
    total_before_vat = subtotal - discount
    vat = total_before_vat * 0.19
    final_total = total_before_vat + vat

    st.metric("Zwischensumme", f"{subtotal:.2f}€")
    st.metric("MwSt. (19%)", f"{vat:.2f}€")
    st.metric("Gesamtsumme", f"{final_total:.2f}€")

    payment_method = st.selectbox("Zahlungsart", ["Bar", "Karte", "Überweisung", "PayPal"])

    if st.button("Rechnung erstellen"):
        if not customer_name or not kfz:
            st.error("Bitte Kundennamen und KFZ-Kennzeichen eingeben.")
        elif not st.session_state.invoice_items:
            st.error("Bitte mindestens eine Rechnungsposition hinzufügen.")
        else:
            # Save customer
            customer = db.get_customer_by_kfz(kfz)
            if not customer:
                customer_id = db.insert_customer(customer_name, kfz, tel)
            else:
                customer_id = customer["id"]

            # Generate invoice number
            latest_invoice_nr = db.get_latest_invoice_number()
            if latest_invoice_nr:
                year = datetime.now().year
                last_number = int(latest_invoice_nr.split("-")[1])
                new_invoice_nr = f"{year}-{last_number + 1:04d}"
            else:
                new_invoice_nr = f"{datetime.now().year}-1001"

            # Save invoice
            invoice_id = db.insert_invoice(
                nr=new_invoice_nr,
                date=datetime.now().strftime("%Y-%m-%d"),
                customer_id=customer_id,
                subtotal=subtotal,
                rabatt=discount,
                mwst=vat,
                total=final_total,
                zahlart=payment_method
            )

            # Save invoice items
            for item in st.session_state.invoice_items:
                db.insert_invoice_item(invoice_id, item["service_name"], item["qty"], item["unit_price"], item["line_total"])

            # Generate PDF
            invoice_data, invoice_items_from_db = db.get_invoice_details(invoice_id)
            customer_data = db.get_customer_by_kfz(kfz)
            pdf = InvoicePDF()
            pdf.create_invoice(invoice_data, customer_data, invoice_items_from_db)
            pdf_filename = f"Rechnung_{customer_name.replace(' ', '_')}_{new_invoice_nr}.pdf"
            pdf.output_pdf(pdf_filename)

            st.success(f"Rechnung {new_invoice_nr} erfolgreich erstellt!")
            with open(pdf_filename, "rb") as f:
                st.download_button("PDF herunterladen", f, file_name=pdf_filename)

            # Clear session state for next invoice
            st.session_state.invoice_items = []

elif choice == "Services verwalten":
    st.subheader("Services verwalten")

    services = db.get_all_services()
    if services:
        services_df = pd.DataFrame(services, columns=["id", "name", "standard_price"])
        st.write(services_df)

    with st.form("new_service_form"):
        new_service_name = st.text_input("Servicename")
        new_service_price = st.number_input("Preis", min_value=0.0, step=0.50)
        submitted = st.form_submit_button("Neuen Service hinzufügen")
        if submitted and new_service_name and new_service_price > 0:
            db.insert_service(new_service_name, new_service_price)
            st.success(f"Service '{new_service_name}' hinzugefügt.")
            st.experimental_rerun()

elif choice == "Kundenhistorie":
    st.subheader("Kundenhistorie")

    customers = db.get_all_customers()
    customer_names = [c["name"] for c in customers]
    selected_customer_name = st.selectbox("Kunde auswählen", [""] + customer_names)

    if selected_customer_name:
        customer = next((c for c in customers if c["name"] == selected_customer_name), None)
        if customer:
            invoices = db.get_invoices_by_customer(customer["id"])
            if invoices:
                invoices_df = pd.DataFrame(invoices, columns=["id", "nr", "date", "total", "zahlart"])
                st.write(invoices_df)
            else:
                st.info("Keine Rechnungen für diesen Kunden gefunden.")

