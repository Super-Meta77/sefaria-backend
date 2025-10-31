from fastapi import APIRouter, HTTPException
from models import User
from typing import List
from passlib.hash import bcrypt

router = APIRouter()

USERS = {}

@router.post("/users/register", response_model=User)
def register(user: User):
    """Register a new user (demo: username must be unique)"""
    if user.username in USERS:
        raise HTTPException(status_code=409, detail="Username already exists")
    hashed = bcrypt.hash(user.hashed_password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed)
    USERS[user.username] = db_user
    return db_user

@router.post("/users/login", response_model=User)
def login(user: User):
    """Demo login (password verified against hash; in production issue JWT)"""
    if user.username not in USERS:
        raise HTTPException(status_code=404, detail="No such user")
    db_user = USERS[user.username]
    if not bcrypt.verify(user.hashed_password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    return db_user

@router.get("/users/{username}", response_model=User)
def get_profile(username: str):
    """Get user profile by username."""
    if username not in USERS:
        raise HTTPException(status_code=404, detail="No such user")
    return USERS[username]

@router.get("/users/", response_model=List[User])
def list_users():
    """List all registered users (dangerous in prod, demo only!)"""
    return list(USERS.values())
