import os
from datetime import datetime, timedelta,date

from fastapi import FastAPI, Request, Form,Query
from fastapi.responses import HTMLResponse,RedirectResponse,JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sqlite3


from app.utils import hash_password, check_password
from app.models import Base, Therapist, Service
from app.models import  Appointment, AdminUser

from sqlalchemy import text
import shutil
from datetime import date


# Ambil path absolut ke folder saat ini
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = "sqlite:///app/seruni.db" 

app = FastAPI()

# Path ke folder static dan template
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# DB setup
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

def generate_time_slots():

    start = datetime.strptime("08:00", "%H:%M")
    end = datetime.strptime("15:00", "%H:%M")
    slots = []
    while start < end:
        slots.append(start.strftime("%H:%M"))
        start += timedelta(minutes=30)
    return slots


@app.get("/api/unavailable-slots", response_class=JSONResponse)
def get_unavailable_slots(therapist_id: int = Query(...), date: str = Query(...)):
    db = SessionLocal()
    bookings = db.query(Appointment).filter(
        Appointment.therapist_id == therapist_id,
        Appointment.date == date
    ).all()
    db.close()

    taken_slots = []

    for b in bookings:
        start = datetime.strptime(b.start_time.strip(), "%H:%M")
        end = datetime.strptime(b.end_time.strip(), "%H:%M")


        # Tambahkan slot 30 menit yang tercover oleh booking
        while start < end:
            taken_slots.append(start.strftime("%H:%M"))
            start += timedelta(minutes=30)

    return list(set(taken_slots))  # remove duplicates if any



@app.get("/", response_class=HTMLResponse)
# async def read_root(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request, "title": "Rumah Sehat Seruni"})
def read_form(request: Request):
    db = SessionLocal()
    therapists = db.query(Therapist).filter_by(is_active=True).all()
    services = db.query(Service).all()
    db.close()
    time_slots = generate_time_slots()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "therapists": therapists,
        "services": services,
        "title": "Rumah Sehat Seruni",
        "time_slots": time_slots

    })

@app.post("/", response_class=HTMLResponse)
async def create_appointment(
    request: Request,
    name: str = Form(...),
    phone: str = Form(...),
    gender: str = Form(...),
    therapist_id: int = Form(...),
    service_id: int = Form(...),
    date: str = Form(...),
    start_time: str = Form(...)
):
    db = SessionLocal()
    therapists = db.query(Therapist).filter_by(is_active=True).all()
    services = db.query(Service).all()

    time_slots = generate_time_slots()
    
    # 1. Tolak jika hari Jumat
    weekday = datetime.strptime(date, "%Y-%m-%d").weekday()
    if weekday == 4:  # Monday = 0, Friday = 4
        db.close()
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "Booking is not allowed on Fridays.",
            "title": "Rumah Sehat Seruni",
            "therapists": therapists,
            "services": services,
            "time_slots": time_slots,
            "form_data": {
            "name": name,
            "phone": phone,
            "gender": gender,
            "therapist_id": therapist_id,
            "service_id": service_id,
            "date": date,
            "start_time": start_time
        }            
        })

    # 2. Validasi gender pelanggan vs terapis
    therapist = db.query(Therapist).filter(Therapist.id == therapist_id).first()
    if therapist.gender != gender:
        db.close()
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": f"Gender mismatch. You can only book a {gender} therapist.",
            "title": "Rumah Sehat Seruni",
            "therapists": therapists,
            "services": services  ,
            "time_slots": time_slots,
            "form_data": {
                "name": name,
                "phone": phone,
                "gender": gender,
                "therapist_id": therapist_id,
                "service_id": service_id,
                "date": date,
                "start_time": start_time
            }                         
        })

    # 3. Cek bentrok jadwal
    service = db.query(Service).filter(Service.id == service_id).first()
    duration_minutes = service.duration
    start_dt = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
    end_dt = start_dt + timedelta(minutes=duration_minutes)
    start_str = start_dt.strftime("%H:%M")
    end_str = end_dt.strftime("%H:%M")

    overlaps = db.query(Appointment).filter(
        Appointment.therapist_id == therapist_id,
        Appointment.date == date,
        Appointment.start_time < end_str,
        Appointment.end_time > start_str
    ).all()

    if overlaps:
        db.close()
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "Selected time slot is already booked for this therapist.",
            "title": "Rumah Sehat Seruni",
            "therapists": therapists,
            "services": services  ,
            "time_slots": time_slots,
            "form_data": {
                "name": name,
                "phone": phone,
                "gender": gender,
                "therapist_id": therapist_id,
                "service_id": service_id,
                "date": date,
                "start_time": start_time
            }                
        })

    # 4. Simpan booking
    booking = Appointment(
        customer_name=name,
        phone=phone,
        gender=gender,
        therapist_id=therapist_id,
        service_id=service_id,
        date=date,
        start_time=start_str,
        end_time=end_str
    )
    db.add(booking)
    db.commit()
    booking_id = booking.id  # ← simpan ID dulu
    db.close()

    # return RedirectResponse("/", status_code=303)
    return RedirectResponse(f"/confirmation?id={booking_id}", status_code=303)

@app.get("/confirmation", response_class=HTMLResponse)
def booking_confirmation(request: Request, id: int = Query(...)):
    db = SessionLocal()
    booking = db.query(Appointment).filter_by(id=id).first()
    therapist = db.query(Therapist).filter_by(id=booking.therapist_id).first()
    service = db.query(Service).filter_by(id=booking.service_id).first()
    db.close()


    whatsapp_message = f"""Hello Admin,
                    Saya baru saja melakukan booking dengan detail:

                    Nama: {booking.customer_name}
                    Nomor: {booking.phone}
                    Tanggal: {booking.date}
                    Jam: {booking.start_time} - {booking.end_time}
                    Terapis: {therapist.name} ({therapist.gender})
                    Layanan: {service.name} ({service.duration} menit)

                    Mohon dikonfirmasi ya, terima kasih 🙏
                    """
    
    return templates.TemplateResponse("confirmation.html", {
        "request": request,
        "booking": booking,
        "therapist": therapist,
        "service": service,
        "whatsapp_message": whatsapp_message
    })


@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    current_username = request.cookies.get("username")
    current_role = request.cookies.get("role")
    if not current_username:
        return RedirectResponse("/login", status_code=303)

    db = SessionLocal()
    therapists = db.query(Therapist).all()
    services = db.query(Service).all()
    admin_users = db.query(AdminUser).all()
    db.close()

    return templates.TemplateResponse("admin.html", {
        "request": request,
        "therapists": therapists,
        "services": services,
        # "user": username,
        # "role": role,
        "admin_users": admin_users,
        "current_username":current_username,
        "current_role":current_role
    })


@app.post("/admin/add-therapist")
def add_therapist(name: str = Form(...), gender: str = Form(...)):
    db = SessionLocal()
    db.add(Therapist(name=name, gender=gender, is_active=True))
    db.commit()
    db.close()
    return RedirectResponse("/admin", status_code=303)

@app.get("/admin/deactivate-therapist")
def deactivate_therapist(id: int = Query(...)):
    db = SessionLocal()
    t = db.query(Therapist).filter_by(id=id).first()
    if t:
        t.is_active = False
        db.commit()
    db.close()
    return RedirectResponse("/admin", status_code=303)

@app.post("/admin/add-service")
def add_service(name: str = Form(...), duration: int = Form(...), price: float = Form(...)):
    db = SessionLocal()
    db.add(Service(name=name, duration=duration, price=price))
    db.commit()
    db.close()
    return RedirectResponse("/admin", status_code=303)

@app.get("/admin/deactivate-service")
def deactivate_service(id: int = Query(...)):
    db = SessionLocal()
    s = db.query(Service).filter_by(id=id).first()
    if s:
        s.name = "[INACTIVE] " + s.name
        db.commit()
    db.close()
    return RedirectResponse("/admin", status_code=303)

@app.get("/admin/edit-therapist", response_class=HTMLResponse)
def edit_therapist_form(request: Request, id: int = Query(...)):
    current_username = request.cookies.get("username")
    current_role = request.cookies.get("role")  
    if not current_username:
        return RedirectResponse("/login", status_code=303)   


    db = SessionLocal()
    therapist = db.query(Therapist).filter_by(id=id).first()
    db.close()
    return templates.TemplateResponse("edit_therapist.html", {
        "request": request,
        "therapist": therapist
    })

@app.post("/admin/edit-therapist")
def edit_therapist_submit(id: int = Form(...), name: str = Form(...), gender: str = Form(...)):
    current_username = request.cookies.get("username")
    current_role = request.cookies.get("role")  
    if not current_username:
        return RedirectResponse("/login", status_code=303)   
        
    db = SessionLocal()
    therapist = db.query(Therapist).filter_by(id=id).first()
    if therapist:
        therapist.name = name
        therapist.gender = gender
        db.commit()
    db.close()
    return RedirectResponse("/admin", status_code=303)

@app.get("/admin/edit-service", response_class=HTMLResponse)
def edit_service_form(request: Request, id: int = Query(...)):

    current_username = request.cookies.get("username")
    current_role = request.cookies.get("role")
    if not current_username:
        return RedirectResponse("/login", status_code=303)


    db = SessionLocal()
    service = db.query(Service).filter_by(id=id).first()
    db.close()
    return templates.TemplateResponse("edit_service.html", {
        "request": request,
        "service": service
    })

@app.post("/admin/edit-service")
def edit_service_submit(id: int = Form(...), name: str = Form(...), duration: int = Form(...), price: float = Form(...)):

    current_username = request.cookies.get("username")
    current_role = request.cookies.get("role")
    if not current_username:
        return RedirectResponse("/login", status_code=303)

    db = SessionLocal()
    service = db.query(Service).filter_by(id=id).first()
    if service:
        service.name = name
        service.duration = duration
        service.price = price
        db.commit()
    db.close()
    return RedirectResponse("/admin", status_code=303)

@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    db = SessionLocal()
    user = db.query(AdminUser).filter_by(username=username).first()
    db.close()

    if user and check_password(password, user.password):

        if not user.is_active:
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "Your account is inactive."
            })

        response = RedirectResponse("/admin", status_code=303)
        response.set_cookie("username", user.username)
        response.set_cookie("role", user.role.value)
        return response
    

    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Invalid credentials"
    })

@app.post("/admin/reset-password")
def reset_password(id: int = Form(...), new_password: str = Form(...), request: Request = None):
    current_role = request.cookies.get("role")
    if current_role != "superadmin":
        # return HTMLResponse("Unauthorized", status_code=403)
        return RedirectResponse("/login", status_code=303)

    db = SessionLocal()
    user = db.query(AdminUser).filter_by(id=id).first()
    if user:
        user.password = hash_password(new_password)
        db.commit()
    db.close()
    return RedirectResponse("/admin", status_code=303)

@app.get("/setup", response_class=HTMLResponse)
def setup_superadmin_form(request: Request):
    db = SessionLocal()
    existing = db.query(AdminUser).count()
    db.close()
    if existing > 0:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("setup.html", {"request": request})

@app.post("/setup")
def setup_superadmin(username: str = Form(...), password: str = Form(...)):
    db = SessionLocal()
    existing = db.query(AdminUser).count()
    if existing == 0:
        user = AdminUser(
            username=username,
            password=hash_password(password),
            role="superadmin"
        )
        db.add(user)
        db.commit()
        db.close()
        response = RedirectResponse("/admin", status_code=303)
        response.set_cookie("username", username)
        response.set_cookie("role", "superadmin")
        return response
    db.close()
    return RedirectResponse("/login", status_code=303)

@app.get("/logout")
def logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie("username")
    response.delete_cookie("role")
    return response


@app.get("/admin/edit-user", response_class=HTMLResponse)
def edit_user_form(request: Request, id: int = Query(...)):

    current_role = request.cookies.get("role")
    current_username = request.cookies.get("username")


    db = SessionLocal()
    user = db.query(AdminUser).filter_by(id=id).first()
    db.close()

    if current_role != "superadmin" and user.role == "superadmin":
        return HTMLResponse("Unauthorized", status_code=403)

    return templates.TemplateResponse("edit_user.html", {
        "request": request,
        "user": user,
        "role": current_role
    })



@app.post("/admin/edit-user")
def edit_user_submit(
    # id: int = Form(...), username: str = Form(...), role: str = Form(...), is_active: bool = Form(...)):
    request: Request,
    id: int = Form(...),
    username: str = Form(...),
    role: str = Form(...),
    is_active: bool = Form(False)
):
    current_user = request.cookies.get("username")
    current_role = request.cookies.get("role")

    db = SessionLocal()
    user    = db.query(AdminUser).filter_by(id=id).first()

    # ✅ Hitung jumlah superadmin aktif
    superadmins = db.query(AdminUser).filter_by(role="superadmin", is_active=True).all()
    is_last_superadmin = (
        len(superadmins) == 1 and superadmins[0].id == user.id
    )

    # ⛔ Blokir kalau sedang mencoba turunkan satu-satunya superadmin
    if is_last_superadmin and role != "superadmin":
        db.close()
        return HTMLResponse("Cannot demote the last active superadmin.", status_code=400)
    
    # Cegah admin mengubah dirinya sendiri jadi superadmin
    if current_user == user.username and current_role != "superadmin" and role == "superadmin":
        db.close()
        return HTMLResponse("Unauthorized role change", status_code=403)
    
    # ⛔️ Admin biasa tidak boleh edit user superadmin
    if current_role != "superadmin" and user.role == "superadmin":
        db.close()
        return HTMLResponse("Unauthorized to edit superadmin.", status_code=403)

    # Cegah admin biasa mengubah role siapa pun
    if current_role != "superadmin" and user.role != role:
        db.close()
        return HTMLResponse("Only superadmin can change roles", status_code=403)
    
    #update data
    if user:
        user.username = username
        user.is_active = is_active
        # user.role = role
        # hanya superadmin yang boleh ubah role
        if current_role == "superadmin":
            user.role = role       
        db.commit()
    db.close()
    return RedirectResponse("/admin", status_code=303)

@app.post("/admin/add-user")
def add_user(username: str = Form(...), password: str = Form(...), role: str = Form(...), request: Request = None):
    current_role = request.cookies.get("role")
    if current_role != "superadmin":
        return HTMLResponse("Unauthorized", status_code=403)

    db = SessionLocal()
    existing = db.query(AdminUser).filter_by(username=username).first()
    if not existing:
        user = AdminUser(
            username=username,
            password=hash_password(password),
            role=role,
            is_active=True
        )
        db.add(user)
        db.commit()
    db.close()
    return RedirectResponse("/admin", status_code=303)

@app.get("/admin/change-password", response_class=HTMLResponse)
def change_password_form(request: Request):

    current_username = request.cookies.get("username")
    current_role = request.cookies.get("role")
    if not current_username :
        return RedirectResponse("/login", status_code=303)

    return templates.TemplateResponse("change_password.html", {
        "request": request,
        "username": current_username,
        "user": current_username,
        "role": current_role,
        "current_username":current_username,
        "current_role": current_role
    })

@app.post("/admin/change-password")
def change_password_submit(
    request: Request,
    old_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    current_username = request.cookies.get("username")
    current_role = request.cookies.get("role")
    if not current_username :
        return RedirectResponse("/login", status_code=303)

    db = SessionLocal()
    user = db.query(AdminUser).filter_by(username=current_username).first()

    if not user or not check_password(old_password, user.password):
        db.close()
        return templates.TemplateResponse("change_password.html", {
        "request": request,
        "username": current_username,
        "user": current_username,
        "role": current_role,
        "error": "Wrong old password."
        })

    if new_password != confirm_password:
        db.close()
        return templates.TemplateResponse("change_password.html", {
            "request": request,
            "username": current_username,
            "user": current_username,
            "role": current_role,
            "error": "New passwords do not match."
        })

    user.password = hash_password(new_password)
    db.commit()
    db.close()

    return RedirectResponse("/admin", status_code=303)



@app.get("/admin/upcoming", response_class=HTMLResponse)
def upcoming_bookings(request: Request):
    current_username = request.cookies.get("username")
    current_role = request.cookies.get("role")    
    if not current_username:
        return RedirectResponse("/login", status_code=303)

    today = date.today()
    end_day = today + timedelta(days=6)

    db = SessionLocal()
    bookings = (
        db.query(Appointment)
        .filter(Appointment.date >= today, Appointment.date <= end_day)
        .order_by(Appointment.date, Appointment.start_time)
        .all()
    )

    therapist_map = {t.id: t.name for t in db.query(Therapist).all()}
    service_map = {s.id: s.name for s in db.query(Service).all()}
    db.close()

    return templates.TemplateResponse("upcoming.html", {
        "request": request,
        "bookings": bookings,
        "therapist_map": therapist_map,
        "service_map": service_map,
        "current_username": current_username,
        "current_role": current_role     
    })

@app.get("/admin/reset-password-form", response_class=HTMLResponse)
def reset_password_form(request: Request, id: int = Query(...)):

    current_username = request.cookies.get("username")
    current_role = request.cookies.get("role")
    if current_role != "superadmin":
        return RedirectResponse("/login", status_code=303)

    db = SessionLocal()
    user = db.query(AdminUser).filter_by(id=id).first()
    db.close()

    return templates.TemplateResponse("reset_password.html", {
        "request": request,
        "user_target": user,
        "user_target_id": id,
        "current_role": current_role,
        "current_username": current_username
    })


@app.post("/admin/reset-password")
def reset_password_submit(
    id: int = Form(...),
    new_password: str = Form(...),
    request: Request = None
    ):


    current_username = request.cookies.get("username")
    current_role = request.cookies.get("role")
    if current_role != "superadmin":
        return RedirectResponse("/login", status_code=303)


    db = SessionLocal()
    user = db.query(AdminUser).filter_by(id=id).first()
    if user:
        user.password = hash_password(new_password)
        db.commit()
    db.close()
    return RedirectResponse("/admin", status_code=303)



@app.get("/admin/reset-system")
def reset_system(request: Request):

    # current_username = request.cookies.get("username")
    # current_role = request.cookies.get("role")
    # if current_role != "superadmin":
    #     return RedirectResponse("/login", status_code=303)
    
    # Demo only: buka untuk publik
    # (optional) tambahkan log untuk keperluan tracking
    print("⚠️ SYSTEM RESET TRIGGERED via PUBLIC PAGE")


    # Step 1: hapus data semua tabel di seruni.db
    db = SessionLocal()
    meta = Base.metadata
    for table in reversed(meta.sorted_tables):
        db.execute(table.delete())
    db.commit()
    db.close()

    # Step 2: salin isi dari seruni_reset.db ke seruni.db
    temp_conn = sqlite3.connect("app/seruni.db")
    reset_conn = sqlite3.connect("app/seruni_reset.db")

    # Aktifkan kemampuan baca tulis antar db
    reset_conn.backup(temp_conn)
    temp_conn.close()
    reset_conn.close()

    # Step 3: update semua tanggal booking jadi hari ini
    db = SessionLocal()
    today_str = date.today().isoformat()
    db.execute(text(f"UPDATE appointments SET date = :today"), {"today": today_str})
    db.commit()
    db.close()

    return RedirectResponse("/admin", status_code=303)
