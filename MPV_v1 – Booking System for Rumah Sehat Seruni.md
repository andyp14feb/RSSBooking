# 📘 Rumah Sehat Seruni – Booking System Documentation

## 🏷️ Project Name:

**Rumah Sehat Seruni Booking System**

---

## 📖 Overview

This is a web-based **massage parlor appointment system** designed for **Rumah Sehat Seruni**.  
Customers can book therapy sessions with specific therapists and services based on availability.

The system also includes a full **admin panel** for managing therapists, services, and admin users.

---

## 🎯 Core Features

### 👥 Customer Booking

- Book a session by choosing:
  
  - Therapist (only those matching gender)
  
  - Service type
  
  - Available time slots (30-minute increments)

- Prevents booking on **Fridays**

- Prevents **double-booking** time slots for the same therapist

- Displays **slot status** (available/selected/unavailable) with clear color codes

- Confirmation page after successful booking

---

### 🛠 Admin Panel

Accessible only after login.

#### 👤 Therapist Management

- Add/Edit/Deactivate therapists

- Gender-based filtering enforced in booking

#### 💆 Service Management

- Add/Edit/Deactivate services

- Set duration and price

#### 🔐 Admin User Management

- View list of admin users (admin / superadmin)

- Superadmin can:
  
  - Add new users
  
  - Edit roles
  
  - Deactivate users
  
  - Reset passwords for others

#### 🔑 Admin Account

- Admin users can:
  
  - Change their own password securely

- Inactive admins **cannot login**

---

## 🧑‍💼 User Roles

| Role         | Access                                                      |
| ------------ | ----------------------------------------------------------- |
| `admin`      | Manage therapists & services, edit own account              |
| `superadmin` | Full access, including managing users & resetting passwords |

---

## 🧾 Booking Constraints

- 🛑 Closed on Fridays

- ⏱️ Time slots: 08:00 to 15:00, every 30 minutes

- ⛔ One therapist = one session per time slot

- ⚖️ Male customers can only book male therapists (and vice versa)

- 💵 Service price and duration affect time blocking

---

## 🧰 Tech Stack

| Layer      | Technology                                       |
| ---------- | ------------------------------------------------ |
| Backend    | FastAPI (Python)                                 |
| Frontend   | HTML + Tailwind CSS                              |
| Database   | SQLite (dev) → MySQL (prod ready)                |
| Templating | Jinja2 Templates                                 |
| Security   | Manual session (cookie-based), with CSRF planned |

---

## 🚀 Deployment

- Currently running via `uvicorn`

- Prepared for Railway / Render / Fly.io deployment

- Configured with virtualenv

- Uses Alembic for DB migration

---

## 📂 Project Structure (simplified)

pgsql

CopyEdit

`/app   ├── main.py                 ← FastAPI core   ├── models.py               ← SQLAlchemy DB models   ├── templates/   │   ├── index.html          ← Booking page   │   ├── admin.html          ← Admin panel   │   ├── confirmation.html   ← Booking success   │   ├── login.html   │   ├── setup.html   │   ├── edit_user.html   │   └── change_password.html   └── static/                 ← (Optional for custom assets)`

---

## ✅ Status: MVP DONE ✅

Ready for:

- Public testing

- Deployment

- Feature enhancement

---

## 🧪 Next Enhancements

- CSRF token security

- Email/WhatsApp notification for new booking

- Booking history viewer for admin

- Dashboard & analytics

- Export to Excel/CSV
