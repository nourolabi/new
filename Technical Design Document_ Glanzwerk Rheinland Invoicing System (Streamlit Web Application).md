# Technical Design Document: Glanzwerk Rheinland Invoicing System (Streamlit Web Application)

## 1. Introduction

This document outlines the detailed technical design for the Glanzwerk Rheinland invoicing system, to be implemented as a web application using Streamlit. The primary goal of this system is to provide a digital solution for the rapid and accurate generation of professional PDF invoices, adhering strictly to the original Glanzwerk design. The system will support multiple services, configurable prices and quantities, optional discounts, and will be deployed for daily operations at the Glanzwerk Rheinland car wash in Neuwied. This design focuses on fulfilling the core requirements outlined in the provided project brief, including precise invoice layout replication, multi-language support (German and Arabic), and robust data management.

## 2. Overall Architecture

The Glanzwerk Rheinland invoicing system will follow a client-server architecture, with Streamlit serving as both the frontend and a lightweight backend. Streamlit's inherent design simplifies development by abstracting away much of the traditional web development complexity, allowing for rapid prototyping and deployment. The application will be primarily stateless from the server's perspective, with user interactions driving data processing and PDF generation. Persistent data will be managed using a local SQLite database, which is suitable for the described scale and deployment scenarios (Streamlit Cloud or private server).

### 2.1. Component Breakdown

*   **Streamlit Application (Frontend & Backend Logic)**: This is the core of the system, handling user input, business logic, and orchestrating data interactions. It will render the user interface, process form submissions, calculate invoice totals, and trigger PDF generation. Streamlit's component-based structure will be leveraged to create an intuitive and responsive user experience.

*   **SQLite Database**: A local SQLite database file (`glanzwerk.db`) will store all persistent data, including customer information, service catalog, invoices, and invoice items. SQLite is chosen for its simplicity, serverless operation, and ease of integration with Python applications. It will reside within the application's deployment environment.

*   **PDF Generation Engine (fpdf2)**: The `fpdf2` Python library will be used for server-side PDF generation. This library is crucial for achieving the pixel-perfect replication of the provided Word invoice template, including precise control over layout, fonts, colors, and table structures. All PDF generation logic will be encapsulated within a dedicated module to ensure maintainability and reusability.

*   **File System**: The application will interact with the file system for saving generated PDF invoices. A designated directory (e.g., `invoices/`) will be used to store these documents, with filenames generated automatically based on customer and date information.

### 2.2. Data Flow

1.  **User Interaction**: Users (reception/service, owner/backoffice) interact with the Streamlit UI to input customer details, select services, adjust prices/quantities, apply discounts, and choose payment methods.
2.  **Data Processing**: Streamlit's backend logic processes the user input, performs calculations (e.g., subtotal, VAT, total), and validates data.
3.  **Database Operations**: Processed data is then used to perform CRUD (Create, Read, Update, Delete) operations on the SQLite database. This includes saving new invoices, retrieving customer history, and managing the service catalog.
4.  **PDF Generation Trigger**: Upon successful invoice creation, the Streamlit application triggers the `fpdf2` module to generate the PDF invoice, passing all necessary data.
5.  **PDF Output**: The `fpdf2` module generates the PDF file, which is then saved to the file system and potentially offered for download or direct printing to the user.
6.  **Reporting (Optional)**: For optional features like daily/monthly reports, data will be queried directly from the SQLite database and presented within the Streamlit UI.

## 3. Data Model

The data model is designed to store all necessary information for invoice generation, customer management, and service catalog. A SQLite database will be used, and the schema will be defined using standard SQL DDL (Data Definition Language).

### 3.1. Tables

Based on the provided brief, the following tables will constitute the core data model:

*   **`customers` Table**:
    *   `id` (INTEGER PRIMARY KEY AUTOINCREMENT): Unique identifier for each customer.
    *   `name` (TEXT NOT NULL): Full name of the customer.
    *   `kfz` (TEXT NOT NULL): Vehicle registration number (KFZ-Kennzeichen).
    *   `tel` (TEXT): Optional telephone number.

*   **`services` Table**:
    *   `id` (INTEGER PRIMARY KEY AUTOINCREMENT): Unique identifier for each service.
    *   `name` (TEXT NOT NULL UNIQUE): Name of the service (e.g., 


Außenreinigung per Hand").
    *   `standard_price` (REAL NOT NULL): Default price for the service.

*   **`invoices` Table**:
    *   `id` (INTEGER PRIMARY KEY AUTOINCREMENT): Unique identifier for each invoice.
    *   `nr` (TEXT NOT NULL UNIQUE): Unique invoice number (e.g., "2025-0001"). This will be automatically generated, starting from 1001.
    *   `date` (TEXT NOT NULL): Date of the invoice (YYYY-MM-DD format).
    *   `customer_id` (INTEGER NOT NULL): Foreign key referencing the `customers` table.
    *   `subtotal` (REAL NOT NULL): Sum of all invoice item line totals before discount and VAT.
    *   `rabatt` (REAL NOT NULL DEFAULT 0.0): Discount amount (either percentage or fixed amount, stored as a calculated value).
    *   `mwst` (REAL NOT NULL): Calculated VAT amount (19%).
    *   `total` (REAL NOT NULL): Final total amount including VAT and after discount.
    *   `zahlart` (TEXT NOT NULL): Payment method (e.g., "Bar", "Karte", "Überweisung", "PayPal").

*   **`invoice_items` Table**:
    *   `id` (INTEGER PRIMARY KEY AUTOINCREMENT): Unique identifier for each invoice item.
    *   `invoice_id` (INTEGER NOT NULL): Foreign key referencing the `invoices` table.
    *   `service_name` (TEXT NOT NULL): Name of the service for this item (can be from `services` table or a free-text entry).
    *   `qty` (REAL NOT NULL): Quantity of the service.
    *   `unit_price` (REAL NOT NULL): Unit price of the service at the time of invoicing.
    *   `line_total` (REAL NOT NULL): Calculated total for this invoice item (qty * unit_price).

### 3.2. Relationships

*   One `customer` can have many `invoices` (one-to-many).
*   One `invoice` can have many `invoice_items` (one-to-many).
*   The `services` table is a lookup table for pre-defined services, but `invoice_items` can also include ad-hoc services not present in the `services` table.

## 4. Core Functionalities

This section details the implementation of the core functionalities as specified in the requirements.

### 4.1. Invoice Creation and Management

#### 4.1.1. User Interface for Invoice Entry

The Streamlit application will present a clear and intuitive interface for invoice creation. This will include:

*   **Customer Input**: Text input fields for customer name and KFZ-Kennzeichen. A search/autocomplete feature could be implemented to quickly find existing customers based on these fields, pre-filling their data if found.
*   **Service Selection**: A multi-select dropdown or a list of checkboxes populated from the `services` table for quick selection of common services. Each selected service will dynamically add a new row to the invoice items section.
*   **Ad-hoc Service Entry**: A dedicated section or button to add a new, custom service. This will include text input for the service description and a numerical input for its price. This allows for flexibility beyond the predefined service catalog.
*   **Invoice Item Management**: Each invoice item row will display the service description, quantity, unit price, and calculated line total. Quantity and unit price fields will be editable, allowing for real-time updates to the line total and overall invoice total. Buttons for adding and removing invoice items will be provided.
*   **Discount Application**: A section for applying discounts, with options for either a percentage-based discount or a fixed amount. The discount will be applied to the subtotal before VAT calculation.
*   **Payment Method Selection**: A dropdown or radio buttons for selecting the payment method (Bar, Karte, Überweisung, PayPal).

#### 4.1.2. Automatic Invoice Numbering

Invoice numbers will be automatically generated and assigned upon saving a new invoice. The numbering will start from 1001 and increment sequentially. The format will be `YYYY-XXXX` (e.g., `2025-1001`). This ensures uniqueness and chronological order. The application will query the `invoices` table to determine the next available invoice number.

#### 4.1.3. Real-time Calculation

All calculations (line totals, subtotal, discount application, VAT calculation, and final total) will be performed in real-time as the user inputs or modifies data. This provides immediate feedback and reduces errors. Streamlit's reactive nature is well-suited for this, as changes to input widgets automatically trigger re-execution of the relevant parts of the script.

### 4.2. PDF Generation

#### 4.2.1. Pixel-Perfect Replication of Word Template

The most critical aspect of the PDF generation is the pixel-perfect replication of the provided Word template. This will involve:

*   **`fpdf2` Library**: Leveraging `fpdf2` for its fine-grained control over PDF elements. This includes setting exact positions for text, images, and lines.
*   **Font Management**: Embedding the exact fonts used in the Word template to ensure consistent typography. If specific fonts are not standard, they will need to be included as assets and registered with `fpdf2`.
*   **Color Palette**: Extracting the precise color codes (RGB or Hex) from the Word template and applying them consistently to text, lines, and table elements.
*   **Layout and Spacing**: Meticulously measuring and replicating the margins, padding, line heights, and element spacing from the Word template. This will likely involve iterative adjustments and visual comparisons.
*   **Table Structure**: Recreating the table structure, including column widths, borders, and alignment, exactly as seen in the Word document. This will require careful calculation of cell dimensions and positioning.
*   **Logo Integration**: The high-resolution Glanzwerk logo will be embedded at the specified position in the header. `fpdf2` supports image embedding, and the logo will be scaled appropriately to match the template.
*   **Address and Contact Information**: The fixed address (`Krasnaer Str. 1, 56566 Neuwied`) and other contact details will be hardcoded or configured and placed precisely as per the template.

#### 4.2.2. Dynamic Content Insertion

The PDF generation module will dynamically insert the following content:

*   **Invoice Details**: Invoice number, date, and due date (if applicable).
*   **Customer Details**: Name and address of the customer.
*   **Invoice Items**: A table populated with the service description, quantity, unit price, VAT per item, and total per item for each service included in the invoice.
*   **Summary Section**: Subtotal, discount amount, calculated 19% VAT, and the final total amount.
*   **Payment Method**: The selected payment method.

#### 4.2.3. Saving and Printing

Upon successful PDF generation, the application will:

*   **Save to File System**: Save the generated PDF to a designated directory (e.g., `invoices/`) with a structured filename (e.g., `Rechnung_<Kunde>_<YYYY-MM-DD>_<InvoiceNumber>.pdf`).
*   **Download Option**: Provide a button for the user to download the generated PDF directly from the web application.
*   **Print Option**: While direct printing from a web application is client-side dependent, the downloaded PDF can be easily printed by the user.

### 4.3. Service Catalog Management

The `services` table will be pre-populated with the provided list of services. The application will include an interface (potentially a separate page or a modal) for managing this catalog. This will allow authorized users to:

*   **Add New Services**: Input a service name and its standard price.
*   **Edit Existing Services**: Modify the name or standard price of an existing service.
*   **Delete Services**: Remove services from the catalog. (Consider soft deletes or checks for services already used in invoices).

### 4.4. Customer History (Optional but Recommended)

If implemented, the customer history feature will allow users to view a list of past invoices for a specific customer. This will involve:

*   **Search by Customer**: A search function (e.g., by name or KFZ-Kennzeichen) to retrieve customer details.
*   **Invoice List**: Displaying a chronological list of invoices associated with the selected customer, including date, services rendered, total amount, and payment method. Each invoice in the list could be clickable to view its details or regenerate the PDF.

### 4.5. Reports (Optional)

For reporting functionalities, the system could provide:

*   **Daily/Monthly Sales**: Summaries of total revenue, number of invoices, and average invoice value for selected periods.
*   **Top Services**: Identification of the most frequently sold or highest-revenue-generating services.

These reports would be generated by querying the `invoices` and `invoice_items` tables and presenting the data in tables or simple charts within the Streamlit UI.

## 5. Technical Implementation Details

### 5.1. Streamlit Application Structure

The Streamlit application will be organized into logical modules to enhance maintainability and readability. A possible structure includes:

```
.glanzwerk_invoicing/
├── app.py                     # Main Streamlit application file
├── db.py                      # Database connection and CRUD operations
├── pdf_generator.py           # PDF generation logic using fpdf2
├── models.py                  # Data models (e.g., dataclasses for invoices, items)
├── utils.py                   # Utility functions (e.g., invoice number generation)
├── config.py                  # Configuration settings (e.g., VAT rate, address)
├── assets/                    # Static assets (logo, fonts)
│   ├── glanzwerk_logo.png
│   └── fonts/
└── requirements.txt           # Python dependencies
```

### 5.2. Database Interaction

*   **`db.py`**: This module will encapsulate all database interactions. It will include functions for:
    *   `init_db()`: To create tables if they don't exist.
    *   `get_db_connection()`: To establish a connection to the SQLite database.
    *   `insert_customer()`, `get_customer()`, `update_customer()`.
    *   `insert_service()`, `get_services()`, `update_service()`, `delete_service()`.
    *   `insert_invoice()`, `get_invoice()`, `get_invoices_by_customer()`, `get_latest_invoice_number()`.
    *   `insert_invoice_item()`.
*   **SQLAlchemy (Optional but Recommended)**: For a more robust and scalable solution, consider using SQLAlchemy ORM (Object Relational Mapper) instead of raw SQL queries. This would provide a more Pythonic way to interact with the database, handle migrations, and improve code readability.

### 5.3. PDF Generation Module (`pdf_generator.py`)

This module will contain a class or functions responsible for generating the PDF. Key considerations:

*   **`InvoicePDF` Class**: A class that inherits from `fpdf.FPDF` and encapsulates all the logic for drawing the invoice elements. This allows for better organization and reusability.
*   **Methods for Sections**: Separate methods for drawing the header, customer details, invoice items table, summary section, and footer. This modularity makes it easier to adjust specific parts of the layout.
*   **Dynamic Sizing**: Implement logic to dynamically adjust table row heights and page breaks for invoices with many items.
*   **Error Handling**: Graceful handling of potential errors during PDF generation (e.g., missing data).

### 5.4. Multi-language Support (German & Arabic)

Implementing multi-language support, especially with RTL (Right-to-Left) for Arabic, requires careful consideration:

*   **Translation Files**: Use a simple key-value pair system (e.g., JSON files or Python dictionaries) for all UI text and static content. Separate files for German (`de.json`) and Arabic (`ar.json`).
*   **Streamlit Session State**: Store the selected language in Streamlit's `st.session_state` to maintain the language choice across user interactions.
*   **Conditional Rendering**: Dynamically load the appropriate translation file based on the selected language.
*   **RTL Support for Arabic**: This is the most challenging aspect. `fpdf2` has some support for RTL text, but careful testing and potentially custom rendering logic will be required to ensure correct alignment and display of Arabic text in the PDF. For the Streamlit UI, specific CSS styling might be needed if Streamlit's native components don't fully support RTL out-of-the-box. Libraries like `streamlit-lottie` or custom HTML components might be explored for more advanced UI control if needed.

### 5.5. UI/UX Considerations

*   **Clean and Modern Design**: Adhere to the 


artistic-technical


artistic-technical" character described in the brief. Use a consistent color scheme derived from the Glanzwerk logo.
*   **Responsive Layout**: Ensure the Streamlit application is usable on different screen sizes, from desktops to tablets.
*   **User Feedback**: Provide clear feedback to the user, such as success messages upon saving an invoice, or error messages for invalid input.
*   **Intuitive Workflow**: The user flow for creating an invoice should be logical and require minimal training.

## 6. Deployment and Maintenance

### 6.1. Deployment Options

*   **Streamlit Cloud**: The simplest deployment option. It allows for direct deployment from a GitHub repository. This is ideal for rapid setup and minimal maintenance overhead. A free tier is available, but for production use, a paid tier might be necessary depending on usage.
*   **Private Server**: For more control and potentially better performance, the application can be deployed on a private server (e.g., a VPS from providers like DigitalOcean, AWS, or a local server). This would involve setting up a web server (like Nginx or Apache) as a reverse proxy to the Streamlit application.

### 6.2. Dependencies

The `requirements.txt` file will list all necessary Python libraries, including:

*   `streamlit`
*   `fpdf2`
*   `pandas` (for data manipulation and potentially reporting)
*   `sqlalchemy` (if used)

### 6.3. Backup and Recovery

A simple backup strategy for the SQLite database is crucial. This can be achieved with a script that periodically copies the `glanzwerk.db` file to a safe location (e.g., a separate backup directory or a cloud storage service). The frequency of backups should be determined based on the volume of transactions.

### 6.4. Maintenance and Updates

Updates to the application (e.g., adding new features, fixing bugs) will be managed through the GitHub repository. For Streamlit Cloud deployments, pushing changes to the main branch can automatically trigger a redeployment. For private server deployments, a CI/CD pipeline could be set up for automated updates.

## 7. Quality Assurance and Testing

To ensure the quality and reliability of the application, the following testing strategies will be employed:

*   **Unit Testing**: Writing unit tests for critical components, such as the PDF generation logic, database operations, and calculation functions. The `pytest` framework is recommended.
*   **Integration Testing**: Testing the interaction between different components, such as the Streamlit UI, the database, and the PDF generator.
*   **User Acceptance Testing (UAT)**: The final application will be tested by the end-users (Glanzwerk staff) to ensure it meets their requirements and is easy to use. This will include verifying the pixel-perfect accuracy of the generated PDFs against the Word template.

## 8. Security and Data Privacy

*   **Data Minimization**: The system will only store the minimum necessary personal data (name, KFZ, optional phone number).
*   **Secure Deployment**: If deployed on a private server, standard security practices (e.g., firewall, regular updates, secure access) will be followed.
*   **Authentication (Optional)**: For enhanced security, especially if deployed publicly, a simple authentication mechanism (e.g., username/password) could be added to restrict access to authorized users. Streamlit has components and community-developed solutions for this.

## 9. Deliverables

Based on this technical design, the final deliverables will be:

1.  **Streamlit Web Application**: A fully functional web application accessible via a URL (either on Streamlit Cloud or a private server).
2.  **GitHub Repository**: The complete source code, including the Streamlit application, database schema, assets (logo, fonts), and `requirements.txt`.
3.  **Installation/User Guide**: A simple document (in German) explaining how to use the application.
4.  **Example Invoices**: A set of generated PDF invoices to demonstrate the system's functionality and accuracy.

This detailed technical design provides a comprehensive roadmap for the development of the Glanzwerk Rheinland invoicing system. By following this design, the resulting Streamlit web application will be robust, maintainable, and will precisely meet the specified requirements.

