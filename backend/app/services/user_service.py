import json
from pathlib import Path

from app.services.auth_service import get_password_hash, verify_password


USERS_FILE = Path(__file__).resolve().parent.parent / "data" / "users.json"


def load_users():
    if not USERS_FILE.exists():
        return []

    with open(USERS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as file:
        json.dump(users, file, indent=4, ensure_ascii=False)


def find_user(username: str):
    users = load_users()

    for user in users:
        if user["username"] == username:
            return user

    return None


def create_user(username: str, password: str):
    users = load_users()

    if find_user(username):
        return None

    hashed_password = get_password_hash(password)

    new_user = {
        "username": username,
        "password": hashed_password
    }

    users.append(new_user)
    save_users(users)

    return new_user


def authenticate_user(username: str, password: str):
    user = find_user(username)

    if not user:
        return None

    if not verify_password(password, user["password"]):
        return None

    return user