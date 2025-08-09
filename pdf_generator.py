from fpdf import FPDF
import os

class InvoicePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        self.set_auto_page_break(auto=True, margin=15)
        self.FONT_PATH = os.path.join(os.path.dirname(__file__), 'assets', 'DejaVuSans.ttf')
        self.add_font("DejaVuSans", "", self.FONT_PATH, uni=True)
        self.set_font("DejaVuSans", "", 10)

    def header(self):
        # Logo
        self.image(os.path.join(os.path.dirname(__file__), 'assets', 'glanzwerk_logo.png'), 10, 8, 33)
        # Font
        self.set_font('DejaVuSans', '', 15)
        # Title
        self.cell(0, 10, 'Rechnung', 0, 1, 'C')
        # Line break
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVuSans', '', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

    def create_invoice(self, invoice_data, customer_data, invoice_items):
        self.alias_nb_pages()
        self.set_font('DejaVuSans', '', 10)

        # Invoice details
        self.cell(0, 5, f"Rechnungsnummer: {invoice_data['nr']}", 0, 1, "L")
        self.cell(0, 5, f"Datum: {invoice_data['date']}", 0, 1, "L")
        self.ln(10)

        # Customer details
        self.set_font('DejaVuSans', '', 12)
        self.cell(0, 5, 'Kunde:', 0, 1, 'L')
        self.set_font('DejaVuSans', '', 10)
        self.cell(0, 5, customer_data['name'], 0, 1, 'L')
        self.cell(0, 5, customer_data['address'], 0, 1, 'L')
        self.cell(0, 5, customer_data['phone'], 0, 1, 'L')
        self.ln(10)

        # Invoice items table header
        self.set_font('DejaVuSans', '', 10)
        self.cell(10, 10, 'Pos', 1, 0, 'C')
        self.cell(80, 10, 'Leistung', 1, 0, 'C')
        self.cell(20, 10, 'Menge', 1, 0, 'C')
        self.cell(30, 10, 'Einzelpreis', 1, 0, 'C')
        self.cell(20, 10, 'Rabatt', 1, 0, 'C')
        self.cell(30, 10, 'Gesamtpreis', 1, 1, 'C')

        total_amount = 0
        for i, item in enumerate(invoice_items):
            service_name = item['service_name']
            quantity = item['qty']
            unit_price = item['price']
            discount = item['discount']

            item_total = (unit_price * quantity) * (1 - discount / 100)
            total_amount += item_total

            self.cell(10, 10, str(i + 1), 1, 0, 'C')
            self.cell(80, 10, service_name, 1, 0, 'L')
            self.cell(20, 10, str(quantity), 1, 0, 'C')
            self.cell(30, 10, f"{unit_price:.2f}€", 1, 0, 'R')
            self.cell(20, 10, f"{discount}%", 1, 0, 'C')
            self.cell(30, 10, f"{item_total:.2f}€", 1, 1, 'R')

        self.ln(10)

        # Total amount
        self.set_font('DejaVuSans', '', 12)
        self.cell(0, 10, f"Gesamtbetrag: {total_amount:.2f}€", 0, 1, 'R')

        # VAT (Example: 19%)
        vat_rate = 0.19
        vat_amount = total_amount * vat_rate
        self.cell(0, 10, f"zzgl. 19% MwSt.: {vat_amount:.2f}€", 0, 1, 'R')
        self.cell(0, 10, f"Rechnungsbetrag inkl. MwSt.: {total_amount + vat_amount:.2f}€", 0, 1, 'R')

        self.output(f"invoice_{invoice_data['nr']}.pdf")


