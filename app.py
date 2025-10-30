import streamlit as st
from flight_system import FlightSystem
from ticket_generator import TicketGenerator
import pandas as pd
import os
from datetime import date
import time

# Predefined Indian cities (for suggestions)
BASE_CITIES = [
    "Delhi", "Mumbai", "Hyderabad", "Chennai", "Bangalore", "Kolkata", "Pune", "Goa",
    "Ahmedabad", "Chandigarh", "Lucknow", "Patna", "Indore", "Coimbatore", "Mangalore",
    "Bhubaneswar", "Ranchi", "Varanasi", "Visakhapatnam", "Jaipur", "Nagpur", "Surat",
    "Thiruvananthapuram", "Vijayawada", "Mysore", "Dehradun", "Trichy", "Madurai",
    "Raipur", "Bhopal"
]

# -------------------- PAGE SETUP --------------------
st.set_page_config(
    page_title="Flight Management System",
    page_icon="✈️",
    layout="wide",
)

st.title("✈️ Flight Management System")
st.markdown("### Efficiently manage flights, bookings, cancellations, and passengers")

# -------------------- INITIALIZE SYSTEM --------------------
system = FlightSystem()
tg = TicketGenerator()

# Merge base cities with any cities present in flights.csv (dynamic)
dynamic_cities = set(BASE_CITIES)
for f in system.flights:
    dynamic_cities.add(f.source)
    dynamic_cities.add(f.destination)
CITIES = sorted(dynamic_cities)

# -------------------- SIDEBAR NAVIGATION --------------------
menu = st.sidebar.radio(
    "Navigation",
    ["👤 User Portal", "🛫 Admin Portal"],
)

# ================================================================
#                        USER PORTAL
# ================================================================
if menu == "👤 User Portal":
    st.header("👤 User Portal")

    # Use a radio/selectbox for user inner navigation so we can programmatically switch
    user_section = st.sidebar.selectbox("User Section", ["Search Flights", "Book Ticket", "Cancel Ticket"], key="user_section_key")

    # If the Book Now button wants to redirect, set st.session_state["user_section"] = "Book Ticket"
    if "redirect_to_book" in st.session_state and st.session_state["redirect_to_book"]:
        # clear redirect and switch to booking
        st.session_state["redirect_to_book"] = False
        st.session_state["user_section_key"] = "Book Ticket"
        user_section = "Book Ticket"

    # -------------------- SEARCH FLIGHTS --------------------
    if user_section == "Search Flights":
        st.subheader("🔍 Search for Flights")

        col1, col2, col3 = st.columns(3)
        with col1:
            # source dropdown (alphabetical)
            source = st.selectbox(
                "Source",
                options=[""] + CITIES,
                index=0,
                key="src_input",
                help="Start typing to filter cities alphabetically"
            )
        with col2:
            # destination dropdown (alphabetical)
            destination = st.selectbox(
                "Destination",
                options=[""] + CITIES,
                index=0,
                key="dest_input",
                help="Start typing to filter cities alphabetically"
            )
        with col3:
            date_search = st.date_input("Select Date", key="date_input_search", value=date.today())

        if st.button("🔎 Search Flights", key="search_btn"):
            if source and destination:
                results = system.search_flights(source, destination, str(date_search))
                if results:
                    st.success(f"Found {len(results)} flight(s)!")
                    for f in results:
                        with st.container():
                            st.markdown(
                                f"""
                                **{f.flight_id}** | 🏙️ {f.source} ➡️ {f.destination}  
                                🕒 {f.time} | 📅 {f.date}  
                                💺 Economy: {f.available_seats['Economy']} (₹{f.get_price_by_class('Economy')})  
                                💼 Business: {f.available_seats['Business']} (₹{f.get_price_by_class('Business')})  
                                🏆 First Class: {f.available_seats['First Class']} (₹{f.get_price_by_class('First Class')})
                                """
                            )
                            # Book Now - redirect to booking
                            if st.button(f"Book Now ({f.flight_id})", key=f"book_{f.flight_id}_search"):
                                st.session_state["book_prefill"] = {"flight_id": f.flight_id, "date": f.date}
                                # set redirect flag and rerun -> booking page will open
                                st.session_state["redirect_to_book"] = True
                                st.rerun()
                else:
                    st.warning("⚠️ No flights found for this route or date.")
            else:
                st.warning("Please enter both Source and Destination.")

    # -------------------- BOOK TICKET --------------------
    elif user_section == "Book Ticket":
        st.subheader("🎫 Book a Flight Ticket")

        prefill_id = ""
        prefill_date = date.today()
        if "book_prefill" in st.session_state:
            prefill_id = st.session_state["book_prefill"].get("flight_id", "")
            try:
                prefill_date = pd.to_datetime(st.session_state["book_prefill"].get("date", str(date.today()))).date()
            except Exception:
                prefill_date = date.today()

        name = st.text_input("Passenger Name", key="book_name_user")
        num_passengers = st.number_input("👥 Number of Passengers", min_value=1, max_value=10, value=1, key="num_passengers_user")
        flight_id = st.text_input("Flight ID", value=prefill_id, key="book_flight_id_user")
        flight_date = st.date_input("Date", value=prefill_date, key="book_date_user")
        flight_class = st.selectbox("Select Class", ["Economy", "Business", "First Class"], key="book_class_user")

        col1, col2 = st.columns(2)
        with col1:
            show_fare_btn = st.button("💰 Show Fare Breakdown", key="show_fare_user")
        with col2:
            confirm_btn = st.button("✅ Confirm & Pay", key="confirm_booking_user")

        if show_fare_btn:
            if flight_id.strip():
                flight = next((f for f in system.flights if f.flight_id == flight_id and f.date == str(flight_date)), None)
                if flight:
                    details = flight.get_price_by_class(flight_class, breakdown=True)
                    total_fare = details["Total Fare"] * num_passengers
                    st.markdown(f"""
                    ### 💰 Fare Summary for **{flight_class}** ({flight.flight_id})
                    | Component | Amount (₹) |
                    |------------|------------:|
                    | Base Fare | {details['Base Fare']} |
                    | Class Multiplier | ×{details['Class Multiplier']} |
                    | Tax (18%) | {details['Tax (18%)']} |
                    | **Total Fare per Passenger** | **₹{details['Total Fare']}** |
                    | **Total ({num_passengers} Passenger(s))** | **₹{total_fare}** |
                    """)
                    st.session_state["pending_booking"] = {
                        "name": name,
                        "flight_id": flight_id,
                        "date": str(flight_date),
                        "class": flight_class,
                        "fare": details["Total Fare"],
                        "num_passengers": num_passengers
                    }
                    st.success("✅ Fare calculated! Click 'Confirm & Pay' to finalize booking.")
                else:
                    st.error("❌ Flight not found for the given date.")
            else:
                st.error("Please enter a valid Flight ID to check fare.")

        if confirm_btn:
            if "pending_booking" in st.session_state:
                booking = st.session_state["pending_booking"]

                for i in range(1, booking["num_passengers"] + 1):
                    passenger_name = f"{booking['name']} #{i}" if booking["num_passengers"] > 1 else booking["name"]
                    msg = system.book_ticket(booking["flight_id"], passenger_name, booking["date"], booking["class"])
                    st.success(msg)

                    ticket_path = tg.generate_ticket(
                        passenger_name,
                        booking["flight_id"],
                        booking["date"],
                        booking["class"],
                        booking["fare"]
                    )

                    with open(ticket_path, "rb") as pdf_file:
                        st.download_button(
                            label=f"📥 Download Ticket ({passenger_name})",
                            data=pdf_file,
                            file_name=os.path.basename(ticket_path),
                            mime="application/pdf",
                            key=f"dl_user_{passenger_name}"
                        )

                total_fare = booking["fare"] * booking["num_passengers"]
                st.success(f"💵 Total Paid: ₹{total_fare}")
                for key in ["book_name_user", "book_class_user", "pending_booking", "book_prefill", "book_flight_id_user"]:
                    if key in st.session_state:
                        try:
                            del st.session_state[key]
                        except Exception:
                            pass
            else:
                st.warning("Please calculate fare first before confirming.")

    # -------------------- CANCEL TICKET --------------------
    elif user_section == "Cancel Ticket":
        st.subheader("❌ Cancel a Ticket (User)")

        name = st.text_input("Passenger Name", key="user_cancel_name")
        flight_id = st.selectbox("Select Flight ID", options=[""] + sorted([f.flight_id for f in system.flights]), key="user_cancel_fid")
        date_cancel = st.date_input("Flight Date", key="user_cancel_date", value=date.today())

        if st.button("Cancel My Ticket", key="user_cancel_btn"):
            msg = system.cancel_ticket(name, flight_id, str(date_cancel))
            if "✅" in msg:
                st.success(msg)
            else:
                st.warning(msg)


# ================================================================
#                        ADMIN PORTAL
# ================================================================
elif menu == "🛫 Admin Portal":
    st.header("🛫 Admin Portal")

    tab1, tab2, tab3 = st.tabs(["➕ Add / Manage Flights", "📋 View All Flights", "📜 View Booked Tickets"])

    # -------------------- ADD FLIGHTS --------------------
    with tab1:
        st.subheader("Add a New Flight")

        with st.form("add_flight_form"):
            fid = st.text_input("Flight ID (e.g., AI101)", key="admin_add_fid")
            src = st.selectbox("Source", options=CITIES, key="admin_add_src")
            dest = st.selectbox("Destination", options=CITIES, key="admin_add_dest")
            time_str = st.text_input("Time (e.g., 10:00 AM)", key="admin_add_time")
            base_price = st.number_input("Base Ticket Price", min_value=1000.0, step=100.0, key="admin_add_price")
            date_val = st.date_input("Date of Flight", key="admin_add_date")
            econ_seats = st.number_input("Economy Seats", min_value=1, step=1, key="admin_add_econ")
            business_seats = st.number_input("Business Seats", min_value=0, step=1, key="admin_add_bus")
            first_class_seats = st.number_input("First Class Seats", min_value=0, step=1, key="admin_add_first")

            submitted = st.form_submit_button("Add Flight")
            if submitted:
                new_flight = {
                    "flight_id": fid,
                    "source": src,
                    "destination": dest,
                    "time": time_str,
                    "base_price": float(base_price),
                    "date": str(date_val),
                    "econ_seats": int(econ_seats),
                    "business_seats": int(business_seats),
                    "first_class_seats": int(first_class_seats)
                }
                system.add_flight(new_flight)
                st.success(f"✅ Flight {fid} added successfully!")
                # refresh city list
                dynamic_cities.add(src)
                dynamic_cities.add(dest)
                CITIES[:] = sorted(dynamic_cities)

    # -------------------- VIEW FLIGHTS --------------------
    with tab2:
        st.subheader("Current Flight Data")
        if st.button("Refresh Flight List", key="admin_refresh_flights"):
            system.load_flights()
            st.rerun()
            
        flight_data = [{
            "Flight ID": f.flight_id,
            "Source": f.source,
            "Destination": f.destination,
            "Time": f.time,
            "Date": f.date,
            "Price": f.base_price,
            "Economy": f.available_seats["Economy"],
            "Business": f.available_seats["Business"],
            "First Class": f.available_seats["First Class"]
        } for f in system.flights]
        st.dataframe(flight_data, use_container_width=True)

        # Delete flight section
        delete_fid = st.selectbox("Select Flight to Delete", options=[""] + [f.flight_id for f in system.flights], key="admin_delete_fid")
        if st.button("Delete Flight", key="admin_delete_btn"):
            if delete_fid:
                system.delete_flight(delete_fid)
                st.success(f"🗑️ Flight {delete_fid} deleted successfully!")
                st.rerun()
            else:
                st.warning("Please select a flight to delete.")

    # -------------------- VIEW BOOKINGS --------------------
    with tab3:
        st.subheader("📜 View Booked Tickets")

        bookings = system.view_all_bookings()
        if not bookings:
            st.info("No bookings found yet.")
        else:
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                filter_flight = st.text_input("Filter by Flight ID", key="admin_filter_fid")
            with col2:
                use_date_filter = st.checkbox("Filter by Date", key="admin_filter_date_chk")
                if use_date_filter:
                    filter_date = st.date_input("Filter by Date", key="admin_filter_date")
                else:
                    filter_date = None
            with col3:
                filter_class = st.selectbox("Filter by Class", ["All", "Economy", "Business", "First Class"], key="admin_filter_class")

            filtered = bookings
            if filter_flight:
                filtered = [b for b in filtered if b["flight_id"].lower() == filter_flight.lower()]
            if filter_date:
                filtered = [b for b in filtered if b["date"] == str(filter_date)]
            if filter_class != "All":
                filtered = [b for b in filtered if b["class"] == filter_class]

            st.dataframe(filtered, use_container_width=True)

            # Admin cancel option
            st.markdown("---")
            valid_flights = sorted({b.get("flight_id", "") for b in bookings if isinstance(b, dict) and "flight_id" in b and b.get("flight_id")})
            cancel_fid = st.selectbox(
                "Select Flight ID to Cancel Booking",
                    options=[""] + valid_flights,
                    key="admin_cancel_fid"
                )
            cancel_name = st.text_input("Enter Passenger Name to Cancel", key="admin_cancel_name")
            if st.button("Cancel Booking (Admin)", key="admin_cancel_btn"):
                if cancel_fid and cancel_name:
                    match = next((b for b in bookings if b["flight_id"] == cancel_fid and b["passenger_name"].lower() == cancel_name.lower()), None)
                    if match:
                        msg = system.cancel_ticket(cancel_name, cancel_fid, match["date"])
                        st.success(msg)
                        st.rerun()
                    else:
                        st.warning("No matching booking found.")
                else:
                    st.warning("Please provide both Flight ID and Passenger Name.")
