#!/usr/bin/env python3
"""
PDF Generator for Professional Invoice
Converts HTML invoice template to PDF format
"""

import weasyprint
from datetime import datetime, timedelta
import os

def generate_invoice_pdf(
    customer_name="[Kundenname]",
    customer_address="[Kundenadresse]", 
    customer_city="[Stadt, PLZ]",
    invoice_number="2025-001",
    invoice_date=None,
    due_date=None,
    service_period=None,
    services=None,
    bank_name="[Bankname]",
    iban="[IBAN-Nummer]",
    bic="[BIC-Code]",
    output_path="professional_invoice.pdf"
):
    """
    Generate a professional PDF invoice
    
    Args:
        customer_name: Name of the customer
        customer_address: Customer address
        customer_city: Customer city and postal code
        invoice_number: Invoice number
        invoice_date: Invoice date (defaults to today)
        due_date: Due date (defaults to 14 days from invoice date)
        service_period: Service period (defaults to invoice month)
        services: List of services with details
        bank_name: Bank name
        iban: IBAN number
        bic: BIC code
        output_path: Output PDF file path
    """
    
    # Set default dates
    if invoice_date is None:
        invoice_date = datetime.now().strftime("%d.%m.%Y")
    
    if due_date is None:
        due_date_obj = datetime.now() + timedelta(days=14)
        due_date = due_date_obj.strftime("%d.%m.%Y")
    
    if service_period is None:
        service_period = datetime.now().strftime("%m/%Y")
    
    # Default services if none provided
    if services is None:
        services = [
            {
                "description": "Innen- & Außenreinigung",
                "quantity": "1",
                "unit_price": "70,00 €",
                "tax": "13,30 €",
                "total": "83,30 €"
            },
            {
                "description": "GlanzWerk Premium Van",
                "quantity": "1", 
                "unit_price": "149,00 €",
                "tax": "28,31 €",
                "total": "177,31 €"
            }
        ]
    
    # Read the HTML template
    template_path = "/home/ubuntu/invoice_project/invoice_template.html"
    with open(template_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    # Replace placeholders with actual data
    html_content = html_content.replace("[Kundenname]", customer_name)
    html_content = html_content.replace("[Kundenadresse]", customer_address)
    html_content = html_content.replace("[Stadt, PLZ]", customer_city)
    html_content = html_content.replace("2025-001", invoice_number)
    html_content = html_content.replace("[Datum]", invoice_date)
    html_content = html_content.replace("[Fälligkeitsdatum]", due_date)
    html_content = html_content.replace("[Leistungszeitraum]", service_period)
    html_content = html_content.replace("[Bankname]", bank_name)
    html_content = html_content.replace("[IBAN-Nummer]", iban)
    html_content = html_content.replace("[BIC-Code]", bic)
    
    # Generate services table rows if custom services provided
    if len(services) != 2:  # If not default services
        services_html = ""
        total_net = 0
        total_tax = 0
        
        for service in services:
            services_html += f"""
                    <tr>
                        <td>{service['description']}</td>
                        <td>{service['quantity']}</td>
                        <td class="amount">{service['unit_price']}</td>
                        <td class="amount">{service['tax']}</td>
                        <td class="amount">{service['total']}</td>
                    </tr>
            """
            
            # Calculate totals (assuming Euro format)
            try:
                net_amount = float(service['unit_price'].replace('€', '').replace(',', '.').strip())
                tax_amount = float(service['tax'].replace('€', '').replace(',', '.').strip())
                total_net += net_amount
                total_tax += tax_amount
            except:
                pass
        
        # Replace the services table content
        old_tbody = html_content[html_content.find('<tbody>'):html_content.find('</tbody>') + 8]
        new_tbody = f"<tbody>{services_html}</tbody>"
        html_content = html_content.replace(old_tbody, new_tbody)
        
        # Update totals if calculated
        if total_net > 0:
            total_gross = total_net + total_tax
            html_content = html_content.replace("219,00 €", f"{total_net:.2f} €".replace('.', ','))
            html_content = html_content.replace("41,61 €", f"{total_tax:.2f} €".replace('.', ','))
            html_content = html_content.replace("260,61 €", f"{total_gross:.2f} €".replace('.', ','))
    
    # Generate PDF
    try:
        # Create WeasyPrint HTML document
        html_doc = weasyprint.HTML(string=html_content, base_url=".")
        
        # Generate PDF with custom styling
        pdf_bytes = html_doc.write_pdf(
            stylesheets=[],
            optimize_images=True,
            pdf_version='1.7'
        )
        
        # Write PDF to file
        with open(output_path, 'wb') as pdf_file:
            pdf_file.write(pdf_bytes)
        
        print(f"✅ PDF invoice generated successfully: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error generating PDF: {str(e)}")
        return False

def main():
    """Main function to generate a sample invoice"""
    
    # Sample data for demonstration
    sample_data = {
        "customer_name": "Max Mustermann",
        "customer_address": "Musterstraße 123",
        "customer_city": "12345 Musterstadt",
        "invoice_number": "2025-001",
        "bank_name": "Muster Bank AG",
        "iban": "DE89 3704 0044 0532 0130 00",
        "bic": "COBADEFFXXX",
        "output_path": "/home/ubuntu/invoice_project/professional_invoice.pdf"
    }
    
    # Generate the PDF
    success = generate_invoice_pdf(**sample_data)
    
    if success:
        print("\n🎉 Professional invoice PDF has been created!")
        print(f"📄 File location: {sample_data['output_path']}")
    else:
        print("\n❌ Failed to generate PDF invoice")

if __name__ == "__main__":
    main()

