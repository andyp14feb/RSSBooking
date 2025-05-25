from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Therapist, Service

# Koneksi ke SQLite
engine = create_engine("sqlite:///seruni.db", echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# Data dummy terapis
therapists = [
    Therapist(name="Andi", gender="male", is_active=True),
    Therapist(name="Budi", gender="male", is_active=True),
    Therapist(name="Dewi", gender="female", is_active=True),
    Therapist(name="Siti", gender="female", is_active=True),
]

# Data dummy layanan
services = [
    Service(name="Pijat Relaksasi", duration=60, price=120000),
    Service(name="Bekam", duration=45, price=90000),
    Service(name="Totok Wajah", duration=30, price=60000),
]

# Tambahkan ke database
session.add_all(therapists + services)
session.commit()
session.close()

print("✅ Dummy data berhasil dimasukkan!")
