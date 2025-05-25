Berikut adalah dokumen perencanaan lengkap untuk sistem booking **Rumah Sehat Seruni**:

---

# 📘 Planning Document – Booking System for *Rumah Sehat Seruni*

## 📌 1. Latar Belakang

Rumah Sehat Seruni adalah usaha layanan pijat dan terapi yang melayani pelanggan setiap hari kecuali Jumat. Untuk meningkatkan efisiensi operasional dan kenyamanan pelanggan, dibutuhkan sistem reservasi online yang memungkinkan pelanggan melakukan pemesanan secara mandiri, memilih terapis, waktu, dan layanan yang tersedia. Sistem ini juga mempermudah pengelolaan jadwal dan data layanan bagi admin.

---

## 🧩 2. Fitur

### 📝 2.1 Form Booking

- Input nama dan gender pelanggan

- Pilih pendekatan:
  
  - Pilih **waktu** → tampilkan **terapis** yang tersedia sesuai gender
  
  - Pilih **terapis** → tampilkan waktu kosongnya

- Pilih **jenis layanan** (durasi dan harga berbeda-beda)

### 📄 2.2 Booking Result

- Tampilkan ringkasan pemesanan:
  
  - Nama pelanggan
  
  - Terapis terpilih
  
  - Tanggal & waktu
  
  - Layanan
  
  - Harga

- Tampilkan status: "Berhasil", "Gagal", atau "Slot Sudah Terisi"

### ⚙️ 2.3 Automatic Availability Checking

- Mengecek:
  
  - Terapis tidak sedang dibooking di waktu yang sama
  
  - Terapis dan pelanggan memiliki gender yang sesuai
  
  - Jadwal tidak berada di hari Jumat
  
  - Jam berada antara 08:00 sampai 15:00
  
  - Durasi layanan cukup dalam slot tersebut

### 🧑‍💼 2.4 Admin Panel

#### - Terapis:

- Tambah, edit, hapus data terapis (nama, gender, status aktif)

#### - Layanan:

- Tambah, edit, hapus layanan (nama layanan, durasi, harga)

---

## 🧰 3. Tech Stack

| Layer       | Tools                         |
| ----------- | ----------------------------- |
| Frontend    | HTML + TailwindCSS            |
| Backend     | FastAPI (Python)              |
| Template    | Jinja2                        |
| Database    | SQLite (dev), MySQL (prod)    |
| Deployment  | Railway                       |
| Admin Panel | Custom route or separate page |

---

## 🚀 4. Deployment Strategy

1. Versi lokal dikembangkan dan diuji menggunakan SQLite

2. Disimpan di GitHub dan dihubungkan dengan Railway

3. Railway akan otomatis deploy dari GitHub (`requirements.txt` dan `Procfile`)

4. Optional: Tambah custom domain jika upgrade Railway plan

---

## 🧱 5. Project Structure

```
rumah-sehat-seruni/
├── app/
│   ├── main.py             # FastAPI app
│   ├── routers/
│   │   ├── booking.py
│   │   └── admin.py
│   ├── templates/
│   │   └── index.html
│   ├── static/
│   │   └── style.css (Tailwind output)
│   └── models.py
├── requirements.txt
├── Procfile
├── README.md
└── .env
```

---

## 🗃️ 6. Data Structure

### `therapists`

| Field     | Type   | Description              |
| --------- | ------ | ------------------------ |
| id        | int    | Primary key              |
| name      | string | Nama terapis             |
| gender    | string | `male` atau `female`     |
| is_active | bool   | Terapis aktif atau tidak |

---

### `services`

| Field    | Type   | Description                  |
| -------- | ------ | ---------------------------- |
| id       | int    | Primary key                  |
| name     | string | Nama layanan                 |
| duration | int    | Durasi layanan (dalam menit) |
| price    | float  | Harga layanan (Rp)           |

---

### `appointments`

| Field           | Type   | Description                    |
| --------------- | ------ | ------------------------------ |
| id              | int    | Primary key                    |
| customer_name   | string | Nama pelanggan                 |
| customer_gender | string | `male` atau `female`           |
| therapist_id    | int    | Foreign key → `therapists.id`  |
| service_id      | int    | Foreign key → `services.id`    |
| date            | date   | Tanggal booking                |
| start_time      | time   | Jam mulai                      |
| end_time        | time   | Jam selesai (auto dari durasi) |

---

## ⛔ 7. Constraints

1. **Booking hanya di hari Sabtu–Kamis** (tidak tersedia hari Jumat)

2. **Jam buka** hanya antara **08:00 sampai 15:00**

3. **Terapis tidak bisa double-booking**

4. **Customer hanya bisa memilih terapis dengan gender yang sama**

5. **Durasi layanan menentukan slot waktu** yang harus tersedia penuh

6. **Harga dan durasi tergantung layanan yang dipilih**

---


