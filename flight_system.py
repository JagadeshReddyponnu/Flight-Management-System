import csv
import os
from collections import deque

# ===============================================================
#                       FLIGHT CLASS
# ===============================================================

class Flight:
    def __init__(self, flight_id, source, destination, time, base_price, date,
                 econ_seats, business_seats, first_class_seats):
        self.flight_id = flight_id
        self.source = source
        self.destination = destination
        self.time = time
        self.base_price = float(base_price)
        self.date = date

        # Seat structure by class
        self.seats = {
            "Economy": int(econ_seats),
            "Business": int(business_seats),
            "First Class": int(first_class_seats)
        }

        # Available seats start as total seats
        self.available_seats = self.seats.copy()
        self.waitlist = deque()

    def get_price_by_class(self, flight_class, breakdown=False):
        """Returns price or breakdown for selected class."""
        multipliers = {
            "Economy": 1.0,
            "Business": 1.5,
            "First Class": 2.0
        }
        tax_rate = 0.18

        base = self.base_price
        class_multiplier = multipliers.get(flight_class, 1.0)
        total = base * class_multiplier
        tax = total * tax_rate
        total_fare = total + tax

        if breakdown:
            return {
                "Base Fare": base,
                "Class Multiplier": class_multiplier,
                "Tax (18%)": round(tax, 2),
                "Total Fare": round(total_fare, 2)
            }
        return round(total_fare, 2)


# ===============================================================
#                     FLIGHT SYSTEM CLASS
# ===============================================================

class FlightSystem:
    def __init__(self):
        self.flights = []
        self.load_flights()

    # -----------------------------------------------------------
    #                     FLIGHT MANAGEMENT
    # -----------------------------------------------------------
    def load_flights(self):
        """Load all flights from data/flights.csv"""
        self.flights.clear()
        flights_path = os.path.join("data", "flights.csv")

        if not os.path.exists(flights_path):
            os.makedirs("data", exist_ok=True)
            with open(flights_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "flight_id", "source", "destination", "time",
                    "base_price", "date", "econ_seats", "business_seats", "first_class_seats"
                ])
            return

        with open(flights_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    flight = Flight(
                        row["flight_id"], row["source"], row["destination"],
                        row["time"], row["base_price"], row["date"],
                        row["econ_seats"], row["business_seats"], row["first_class_seats"]
                    )
                    self.flights.append(flight)
                except KeyError:
                    continue

    def save_flights(self):
        """Save all flights back to data/flights.csv"""
        os.makedirs("data", exist_ok=True)
        with open("data/flights.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "flight_id", "source", "destination", "time",
                "base_price", "date", "econ_seats", "business_seats", "first_class_seats"
            ])
            for fobj in self.flights:
                writer.writerow([
                    fobj.flight_id, fobj.source, fobj.destination, fobj.time,
                    fobj.base_price, fobj.date,
                    fobj.seats["Economy"], fobj.seats["Business"], fobj.seats["First Class"]
                ])

    def add_flight(self, new_flight):
        """Add a new flight to the system."""
        flight_obj = Flight(
            new_flight["flight_id"], new_flight["source"], new_flight["destination"],
            new_flight["time"], new_flight["base_price"], new_flight["date"],
            new_flight["econ_seats"], new_flight["business_seats"], new_flight["first_class_seats"]
        )
        self.flights.append(flight_obj)
        self.save_flights()

    def delete_flight(self, flight_id):
        """Remove a flight by ID."""
        self.flights = [f for f in self.flights if f.flight_id != flight_id]
        self.save_flights()

    # -----------------------------------------------------------
    #                     SEARCH FUNCTIONALITY
    # -----------------------------------------------------------
    def search_flights(self, source, destination, date):
        """Search flights by source, destination, and date."""
        return [
            f for f in self.flights
            if f.source.lower() == source.lower()
            and f.destination.lower() == destination.lower()
            and f.date == date
        ]

    # -----------------------------------------------------------
    #                     BOOKING SYSTEM
    # -----------------------------------------------------------
    def book_ticket(self, flight_id, passenger_name, flight_date, flight_class):
        """Book a ticket or add to waitlist."""
        for flight in self.flights:
            if flight.flight_id == flight_id and flight.date == flight_date:
                if flight.available_seats[flight_class] > 0:
                    flight.available_seats[flight_class] -= 1
                    self._record_booking(passenger_name, flight_id, flight_date, flight_class)
                    self.save_flights()
                    return f"✅ Booking confirmed for {passenger_name} ({flight_class}) on {flight_id}."
                else:
                    flight.waitlist.append(passenger_name)
                    self._record_waitlist(passenger_name, flight_id, flight_date, flight_class)
                    return f"🕓 No seats available. {passenger_name} added to waitlist for {flight_id}."
        return "❌ Flight not found."

    def _record_booking(self, passenger_name, flight_id, flight_date, flight_class):
        """Save booking info to bookings.csv"""
        os.makedirs("data", exist_ok=True)
        bookings_path = os.path.join("data", "bookings.csv")
        exists = os.path.exists(bookings_path)

        with open(bookings_path, "a", newline="") as f:
            writer = csv.writer(f)
            if not exists:
                writer.writerow(["passenger_name", "flight_id", "date", "class", "fare"])
            fare = next(
                (fobj.get_price_by_class(flight_class) for fobj in self.flights if fobj.flight_id == flight_id),
                0
            )
            writer.writerow([passenger_name, flight_id, flight_date, flight_class, fare])

    def _record_waitlist(self, passenger_name, flight_id, flight_date, flight_class):
        """Record passengers in waitlist.csv"""
        os.makedirs("data", exist_ok=True)
        waitlist_path = os.path.join("data", "waitlist.csv")
        exists = os.path.exists(waitlist_path)
        with open(waitlist_path, "a", newline="") as f:
            writer = csv.writer(f)
            if not exists:
                writer.writerow(["passenger_name", "flight_id", "date", "class"])
            writer.writerow([passenger_name, flight_id, flight_date, flight_class])

    # -----------------------------------------------------------
    #                     CANCEL TICKET
    # -----------------------------------------------------------
    def cancel_ticket(self, passenger_name, flight_id, flight_date):
        """Cancel a passenger ticket and free up seat — fully safe version."""
        bookings_path = os.path.join("data", "bookings.csv")

        # If no bookings file exists
        if not os.path.exists(bookings_path):
            return "⚠️ No bookings found to cancel."

        updated_bookings = []
        cancelled = False
        cancelled_class = None

        with open(bookings_path, "r", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)

            if not rows:
                return "⚠️ No bookings available."

            # Detect if headers exist
            headers = rows[0]
            if "passenger_name" in headers:
                data_rows = rows[1:]
            else:
                # Create headers manually if missing
                headers = ["passenger_name", "flight_id", "date", "class", "fare"]
                data_rows = rows

            for row in data_rows:
                if len(row) < 5:
                    continue
                pname, fid, fdate, fclass, fare = row[:5]

                if (
                    pname.strip().lower() == passenger_name.strip().lower()
                    and fid.strip() == flight_id
                    and fdate.strip() == flight_date
                ):
                    cancelled = True
                    cancelled_class = fclass
                    continue
                updated_bookings.append(row)

        # Rewrite file
        with open(bookings_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(updated_bookings)

        if cancelled:
            # Free up seat in the relevant flight
            for f in self.flights:
                if f.flight_id == flight_id and f.date == flight_date:
                    f.available_seats[cancelled_class] += 1

            self.save_flights()
            return f"✅ Booking for {passenger_name} on flight {flight_id} cancelled successfully!"
        else:
            return "❌ No matching booking found."

    # -----------------------------------------------------------
    #                     VIEW BOOKINGS
    # -----------------------------------------------------------
    def view_all_bookings(self):
        """Return all bookings as a list of dicts."""
        bookings_path = os.path.join("data", "bookings.csv")
        if not os.path.exists(bookings_path):
            return []
        with open(bookings_path, "r") as f:
            reader = csv.DictReader(f)
            return list(reader)
