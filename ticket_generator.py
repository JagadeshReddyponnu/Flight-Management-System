from fpdf import FPDF
import os
from datetime import datetime
import qrcode

class TicketGenerator:
    def generate_ticket(self, passenger_name, flight_id, flight_date, flight_class, fare):
        # Make sure folders exist
        os.makedirs("fonts", exist_ok=True)
        os.makedirs("tickets", exist_ok=True)

        pdf = FPDF()
        pdf.add_page()

        # ✅ Use Unicode font
        font_path = os.path.join("fonts", "DejaVuSans.ttf")
        if not os.path.exists(font_path):
            raise FileNotFoundError("Font 'DejaVuSans.ttf' not found in fonts folder.")

        pdf.add_font("DejaVu", "", font_path, uni=True)
        pdf.set_font("DejaVu", size=16)

        # ---- Header ----
        pdf.cell(200, 15, "AirVara Airlines ✈️", ln=True, align="C")
        pdf.set_font("DejaVu", size=12)
        pdf.ln(5)
        pdf.cell(200, 10, f"Issue Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
        pdf.ln(10)

        # ---- Passenger Details ----
        pdf.cell(0, 10, f"Passenger Name: {passenger_name}", ln=True)
        pdf.cell(0, 10, f"Flight ID: {flight_id}", ln=True)
        pdf.cell(0, 10, f"Flight Date: {flight_date}", ln=True)
        pdf.cell(0, 10, f"Class: {flight_class}", ln=True)
        pdf.cell(0, 10, f"Fare Paid: ₹{fare}", ln=True)
        pdf.ln(10)

        # ---- QR Code ----
        ticket_data = f"{passenger_name}|{flight_id}|{flight_date}|{flight_class}|₹{fare}"
        qr = qrcode.make(ticket_data)
        qr_path = os.path.join("tickets", f"{passenger_name}_{flight_id}_qr.png")
        qr.save(qr_path)
        pdf.image(qr_path, x=160, y=60, w=35)

        # ---- Footer ----
        pdf.ln(20)
        pdf.set_font("DejaVu", size=11)
        pdf.cell(0, 10, "Thank you for flying with AirVara Airlines!", ln=True, align="C")
        pdf.cell(0, 10, "For support: support@airvara.com", ln=True, align="C")

        # ---- Save Ticket ----
        ticket_path = os.path.join("tickets", f"{passenger_name}_{flight_id}.pdf")
        pdf.output(ticket_path)

        return ticket_path
