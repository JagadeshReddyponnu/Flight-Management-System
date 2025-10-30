Perfect, JAGADESH ✅
Your GitHub repo is successfully connected and `.gitignore` is working — great progress! 🎉

Now let’s make your repo **look professional** with a detailed `README.md`.
Copy the following text and paste it into a new file named **`README.md`** inside your project folder (`FlightManagementSystem`).

---

## 🛫 Flight Management System ✈️

### 📘 Overview

The **Flight Management System** is a Streamlit-based application designed to simulate a real-world airline management system. It includes features for both users and admins — such as searching, booking, cancelling flights, and managing passenger data.

It’s built to demonstrate strong **Python**, **Streamlit**, **File Handling (CSV)**, and **Data Management** skills.

---

### 🧠 Key Features

#### 👤 User Portal

* 🔍 Search for available flights by source, destination, and date
* 🎫 Book flight tickets (Economy / Business / First Class)
* 🧾 Download PDF tickets with unique QR codes
* ❌ Cancel booked tickets
* 📅 View available flights dynamically by city or date

#### 🧑‍💼 Admin Portal

* ➕ Add, update, or delete flights
* 📋 View and filter all current flights
* 📜 View all booked tickets with filters by class/date/flight ID
* 🗑️ Cancel bookings from the admin panel
* 🔄 Auto-refresh flight and booking data

---

### 🛠️ Tech Stack

| Component     | Technology                                    |
| ------------- | --------------------------------------------- |
| Frontend      | Streamlit                                     |
| Backend       | Python 3.11                                   |
| Database      | CSV (bookings.csv, flights.csv, waitlist.csv) |
| PDF & QR      | fpdf2, qrcode                                 |
| Visualization | Pandas, Streamlit UI                          |
| Font Support  | DejaVu Sans (for ₹ & Unicode)                 |

---

### ⚙️ Installation

#### 1️⃣ Clone this repository

```bash
git clone https://github.com/JagadeshReddyponnu/Flight-Management-System.git
cd Flight-Management-System
```

#### 2️⃣ Create and activate virtual environment

```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux
```

#### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

#### 4️⃣ Run the app

```bash
streamlit run app.py
```

---

### 📦 Folder Structure

```
FlightManagementSystem/
│
├── app.py                    # Main Streamlit UI
├── flight_system.py          # Core flight and booking logic
├── ticket_generator.py       # Ticket creation and QR handling
├── utils.py                  # Helper utilities
│
├── data/
│   ├── flights.csv
│   ├── bookings.csv
│   └── waitlist.csv
│
├── assets/
│   └── banner.jpg
│
├── fonts/
│   └── DejaVuSans.ttf
│
├── tickets/                  # Generated tickets (PDFs)
│
└── requirements.txt
```

---

### 🧾 Example Flight Data

| Flight ID | Source    | Destination | Time  | Base Price | Date       | Economy | Business | First Class |
| --------- | --------- | ----------- | ----- | ---------- | ---------- | ------- | -------- | ----------- |
| AI101     | Hyderabad | Delhi       | 06:30 | 5200       | 2025-11-02 | 30      | 10       | 5           |
| AI102     | Delhi     | Mumbai      | 09:00 | 4800       | 2025-11-02 | 25      | 8        | 3           |
| AI103     | Bangalore | Chennai     | 14:00 | 4400       | 2025-11-03 | 35      | 9        | 4           |

---

### 🎨 UI Preview

(Add your screenshot here once your app runs successfully)

```markdown
![Flight Management UI](assets/banner.jpg)
```

---

### 👨‍💻 Author

**Jagadesh Reddy Ponnu**
🎓 B.Tech CSE, Lovely Professional University
💼 Passionate about AI, Data, and Scalable Software Systems

---

