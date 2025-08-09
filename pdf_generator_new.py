from fpdf import FPDF
import os
import tempfile
from datetime import datetime, timedelta

class GlanzwerkInvoicePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        # Company header line
        self.set_font('Arial', '', 10)
        self.cell(0, 5, 'Glanzwerk Rheinland, Krasnaer Str. 1, 56566 Neuwied, Deutschland', 0, 1, 'L')
        self.ln(5)
        
    def footer(self):
        self.set_y(-40)
        
        # Footer with company details
        self.set_font('Arial', '', 9)
        
        # Left column
        self.cell(60, 4, 'Glanzwerk Rheinland', 0, 0, 'L')
        self.cell(70, 4, 'Glanzwerk.Rheinland@gmail.com', 0, 0, 'L')
        self.cell(60, 4, 'Bankverbindung:', 0, 1, 'L')
        
        self.cell(60, 4, 'Krasnaer Str. 1', 0, 0, 'L')
        self.cell(70, 4, '+49 171 1858241', 0, 0, 'L')
        self.cell(60, 4, 'Bank: Sparkasse Neuwied', 0, 1, 'L')
        
        self.cell(60, 4, '56566 Neuwied', 0, 0, 'L')
        self.cell(70, 4, 'Instagram: @glanzwerk_rheinland', 0, 0, 'L')
        self.cell(60, 4, 'IBAN: DE89 5745 0120 0000 1234 56', 0, 1, 'L')
        
        self.cell(60, 4, 'Deutschland', 0, 0, 'L')
        self.cell(70, 4, '', 0, 0, 'L')
        self.cell(60, 4, 'BIC: MALADE51NWD', 0, 1, 'L')
        
    def customer_address(self, customer_name, vehicle_number):
        # Customer address section
        self.set_font('Arial', '', 11)
        self.cell(0, 6, customer_name, 0, 1, 'L')
        self.cell(0, 6, f'Fahrzeug: {vehicle_number}', 0, 1, 'L')
        self.ln(5)
        
    def invoice_header(self, invoice_number):
        # Invoice details in right column
        current_date = datetime.now()
        due_date = current_date + timedelta(days=14)
        
        # Position for right-aligned content
        self.set_xy(120, 35)
        self.set_font('Arial', '', 11)
        
        self.cell(70, 6, f'Rechnungsnummer: {invoice_number}', 0, 1, 'L')
        self.set_x(120)
        self.cell(70, 6, f'Rechnungsdatum: {current_date.strftime("%d.%m.%Y")}', 0, 1, 'L')
        self.set_x(120)
        self.cell(70, 6, f'Fälligkeitsdatum: {due_date.strftime("%d.%m.%Y")}', 0, 1, 'L')
        
        # Reset position for main content
        self.set_xy(10, 70)
        
    def invoice_title(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'RECHNUNG', 0, 1, 'L')
        self.ln(5)
        
    def greeting_text(self):
        self.set_font('Arial', '', 11)
        self.cell(0, 6, 'Sehr geehrte Damen und Herren,', 0, 1, 'L')
        self.ln(3)
        self.cell(0, 6, 'vielen Dank für Ihre Inanspruchnahme unserer Dienstleistungen bei Glanzwerk Rheinland.', 0, 1, 'L')
        self.cell(0, 6, 'Nachfolgend finden Sie die Details Ihrer Rechnung:', 0, 1, 'L')
        self.ln(8)
        
    def service_table(self, invoice_data):
        # Table header
        self.set_font('Arial', 'B', 11)
        self.cell(80, 8, 'Beschreibung', 1, 0, 'L')
        self.cell(25, 8, 'Anzahl/Art', 1, 0, 'C')
        self.cell(25, 8, 'Einzelpreis', 1, 0, 'R')
        self.cell(25, 8, 'MwSt.', 1, 0, 'R')
        self.cell(25, 8, 'Gesamt', 1, 1, 'R')
        
        # Service row
        self.set_font('Arial', '', 10)
        service_description = self.get_service_description(invoice_data['service'])
        gross_before_discount = invoice_data['net_price'] + invoice_data['tax_amount']
        
        self.cell(80, 8, service_description, 1, 0, 'L')
        self.cell(25, 8, '1', 1, 0, 'C')
        self.cell(25, 8, f"{invoice_data['net_price']:.0f}EUR", 1, 0, 'R')
        self.cell(25, 8, f"{invoice_data['tax_amount']:.2f}EUR", 1, 0, 'R')
        self.cell(25, 8, f"{gross_before_discount:.2f}EUR", 1, 1, 'R')
        
        # Discount row if applicable
        if invoice_data['discount_applied']:
            self.cell(80, 8, 'Stammkundenrabatt (10%)', 1, 0, 'L')
            self.cell(25, 8, '1', 1, 0, 'C')
            self.cell(25, 8, '', 1, 0, 'R')
            self.cell(25, 8, '', 1, 0, 'R')
            self.cell(25, 8, f"-{invoice_data['discount_amount']:.2f}EUR", 1, 1, 'R')
        
        # Total row
        self.set_font('Arial', 'B', 11)
        self.cell(155, 10, 'Gesamt inkl. MwSt.', 1, 0, 'R')
        self.cell(25, 10, f"{invoice_data['total_price']:.2f}EUR", 1, 1, 'R')
        
        self.ln(8)
        
    def get_service_description(self, service):
        descriptions = {
            'Grundreinigung': 'Innen- & Außenreinigung\nStandard',
            'Intensivreinigung': 'Innen- & Außenreinigung\nIntensiv',
            'Premium-Wäsche': 'GlanzWerk Premium\nKomplett-Service'
        }
        return descriptions.get(service, service)
        
    def payment_info(self):
        self.set_font('Arial', '', 10)
        
        # Payment method
        self.cell(0, 6, 'Bezahlung durch: [Bar / Überweisung / PayPal]', 0, 1, 'L')
        self.ln(3)
        
        # Payment terms
        self.cell(0, 6, 'Sofern nichts anderes angegeben ist, entspricht der Monat des', 0, 1, 'L')
        self.cell(0, 6, 'Rechnungsdatums dem Leistungszeitpunkt.', 0, 1, 'L')
        self.ln(3)
        
        due_date = (datetime.now() + timedelta(days=14)).strftime("%d.%m.%Y")
        self.cell(0, 6, f'Bitte überweisen Sie den Betrag bis spätestens {due_date}', 0, 1, 'L')
        self.ln(5)
        
        # Closing text
        self.cell(0, 6, 'Bei Fragen stehen wir Ihnen gerne zur Verfügung.', 0, 1, 'L')
        self.cell(0, 6, 'Wir danken Ihnen für Ihr Vertrauen und freuen uns auf eine weitere Zusammenarbeit.', 0, 1, 'L')
        self.ln(8)
        
        # Signature
        self.cell(0, 6, 'Mit freundlichen Grüßen,', 0, 1, 'L')
        self.cell(0, 6, 'Glanzwerk Rheinland', 0, 1, 'L')

def generate_invoice_pdf_new(invoice_data):
    """Generiert eine PDF-Rechnung im neuen Design"""
    pdf = GlanzwerkInvoicePDF()
    pdf.add_page()
    
    # Generiere Rechnungsnummer basierend auf Zeitstempel
    invoice_number = f"2025-{datetime.now().strftime('%m%d%H%M')}"
    
    # Customer address
    pdf.customer_address(invoice_data['customer_name'], invoice_data['vehicle_number'])
    
    # Invoice header with numbers and dates
    pdf.invoice_header(invoice_number)
    
    # Invoice title
    pdf.invoice_title()
    
    # Greeting text
    pdf.greeting_text()
    
    # Service table
    pdf.service_table(invoice_data)
    
    # Payment information
    pdf.payment_info()
    
    # Speichere in temporärer Datei
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(temp_file.name)
    
    return temp_file.name

