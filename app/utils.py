import hashlib

def hash_password(raw: str):
    return hashlib.sha256(raw.encode()).hexdigest()

def check_password(raw: str, hashed: str):
    return hash_password(raw) == hashed
