"""
Securite du noyau.

Deux usages coexistent dans cette application :
- l'API (utilisee par les scripts, les tests, et par les agents via leur
  tenant_api_key) s'authentifie avec un jeton JWT dans l'en-tete
  Authorization: Bearer ... ;
- les pages web (inscription, catalogue, tableau de bord, admin) sont
  consultees depuis un navigateur : le meme jeton JWT y est simplement
  stocke dans un cookie plutot que dans un en-tete, pour eviter d'avoir
  a reecrire une seconde logique d'authentification.

generate_tenant_api_key() produit les cles distinctes remises aux agents
(une par couple entreprise/agent), qui n'ont rien a voir avec les jetons
JWT des utilisateurs.
"""
import os
import secrets
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Role

COOKIE_NAME = "access_token"

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_ME_IN_PRODUCTION")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def generate_tenant_api_key() -> str:
    """Clé unique remise à un agent pour représenter (tenant, agent)."""
    return f"tak_{secrets.token_urlsafe(32)}"


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()  # noqa: E712
    if user is None:
        raise credentials_exception
    return user


def require_role(*allowed_roles: Role):
    """Dépendance FastAPI pour restreindre un endpoint à certains rôles."""
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès refusé : rôle insuffisant"
            )
        return user
    return checker


def _decode_user(token: str, db: Session) -> User | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
    except JWTError:
        return None
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id, User.is_active == True).first()  # noqa: E712


def get_user_from_cookie(request: Request, db: Session = Depends(get_db)) -> User | None:
    """
    Pour les pages web uniquement. Ne leve pas d'exception : renvoie None
    si personne n'est connecte, a charge de la route de decider (afficher
    un lien de connexion, ou rediriger vers /connexion).
    """
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    return _decode_user(token, db)


def require_same_company_or_admin(company_id: str, user: User = Depends(get_current_user)) -> User:
    """
    Empêche un company_admin/user d'accéder aux données d'une autre
    entreprise. Utilisable directement en Depends(...) sur toute route
    dont le paramètre de chemin s'appelle `company_id` : FastAPI résout
    automatiquement `company_id` depuis l'URL.
    """
    if user.role == Role.PLATFORM_ADMIN:
        return user
    if str(user.company_id) != str(company_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Isolation multi-tenant : accès interdit à cette entreprise"
        )
    return user
