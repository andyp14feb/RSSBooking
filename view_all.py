from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Therapist, Service, Appointment

# Setup koneksi ke database SQLite
engine = create_engine("sqlite:///seruni.db", echo=False)
Session = sessionmaker(bind=engine)
session = Session()

print("🧘 Therapists:")
for t in session.query(Therapist).all():
    print(f"  - {t.name} ({t.gender}) | Active: {t.is_active}")

print("\n💆 Services:")
for s in session.query(Service).all():
    print(f"  - {s.name} | {s.duration} min | Rp {s.price:,.0f}")

print("\n📅 Appointments:")
for a in session.query(Appointment).all():
    print(f"  - {a.customer_name} - {a.date} {a.start_time} → {a.end_time} with Therapist ID {a.therapist_id}")

session.close()
