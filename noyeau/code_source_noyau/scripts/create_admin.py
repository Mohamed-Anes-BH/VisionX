"""
A executer une seule fois, apres le premier lancement du noyau, pour
creer le compte administrateur de la plateforme (l'enseignant).

Usage :
    python scripts/create_admin.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal
from app.models import User, Role
from app.core.security import hash_password


def main():
    email = input("Email de l'administrateur : ").strip()
    full_name = input("Nom complet : ").strip()
    password = input("Mot de passe : ").strip()

    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == email).first():
            print("Un compte avec cet email existe deja.")
            return

        admin = User(
            email=email,
            full_name=full_name,
            hashed_password=hash_password(password),
            role=Role.PLATFORM_ADMIN,
            company_id=None,
        )
        db.add(admin)
        db.commit()
        print(f"Compte administrateur cree pour {email}.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
