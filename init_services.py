import db

# Initialize the database
db.init_db()

# List of services from the requirements
services = [
    ("Außenreinigung per Hand", 25.00),
    ("Felgenreinigung & Flugrostentfernung", 35.00),
    ("Innenraumreinigung", 30.00),
    ("Lederreinigung & -pflege", 45.00),
    ("Lederreparatur", 80.00),
    ("Polster- & Teppichreinigung", 40.00),
    ("Scheibenreinigung innen & außen", 15.00),
    ("Lackpolitur & Glanzversiegelung", 120.00),
    ("Nano-Keramik-Versiegelung", 200.00),
    ("Motorraumreinigung", 50.00),
    ("Geruchsneutralisierung & Ozonbehandlung", 60.00),
    ("Tierhaarentfernung", 35.00),
    ("Hagelschaden- und Dellenentfernung (Ausbeulen ohne Lackieren)", 150.00),
    ("Auto Folieren", 300.00),
    ("Abhol- und Bringservice", 20.00),
    ("Innen- & Außenreinigung", 70.00),
    ("GlanzWerk Premium Van", 149.00)
]

# Insert services into the database
for service_name, price in services:
    try:
        db.insert_service(service_name, price)
        print(f"Service '{service_name}' added with price {price}€")
    except Exception as e:
        print(f"Service '{service_name}' already exists or error: {e}")

print("Services initialization completed.")

