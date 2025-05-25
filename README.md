# 🏠 Rumah Sehat Seruni – Booking App

This is a **practicum/demo project** for the online course:

> **Ngoding Pakai `</AI>` – by Inovasia.minicourse**  

As part of the requirement to complete the 6 hours mini course and earn the certificate,  
this project serves as the final practicum submission.

---

## 🌐 Online Demo

👉 https://rssbooking-production.up.railway.app/

---

## 📦 Sreenshots

![JustAScreenshot](https://github.com/andyp14feb/RSSBooking/blob/main/2025-05-25_100436_001__ScreenShots.jpg)


---

## 📦 What This App Does

This is a **web-based booking system** for a massage parlor (Rumah Sehat Seruni), allowing customers to book therapy sessions with the following features:

### 🧑‍💼 User Features

- Book available therapy sessions (08:00 to 15:00 daily except Friday)
- Choose available therapist by gender match (male → male therapist, etc.)
- Pick service type and duration
- Real-time booking slot availability (30-minute intervals)
- WhatsApp confirmation link with all booking details

### 🔐 Admin Features

- Admin login system with Superadmin role
- Manage therapists (add/edit/deactivate)
- Manage services and pricing
- View booking summary (next 7 days)
- Reset system data to default (for demo)
- Admin password reset (own or by superadmin)

---

## 🚀 How to Install and Run Locally

### 1. Clone this repository

```bash
git clone https://github.com/your-username/RSSBooking.git
cd RSSBooking
```

### 2. Create virtual environment & activate it

```bash
python -m venv .venv
.\.venv\Scripts\activate   # For Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
uvicorn app.main:app --reload
```

App will be available at:  
➡️ `http://localhost:8000`

---

## 🧪 For Demo Purposes

This app is preloaded with demo data from `seruni.db` (SQLite).  
You can reset the system state by visiting:

https://rssbooking-production.up.railway.app/admin/reset-system`

---

## 🛠 Tech Stack

- Backend: **FastAPI**
  
- Templating: **Jinja2 + TailwindCSS**
  
- DB: **SQLite (local)** via SQLAlchemy ORM
  
- Deployment: **Railway (Docker-based)**
  

---

## 📚 License

MIT License – free to use and modify for learning or personal projects.
