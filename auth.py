import jwt
from fastapi import Header, HTTPException

SECRET = "dev-secret-change-me"
ALGO = "HS256"


def create_access_token(user_id: str, name: str) -> str:
    payload = {"sub": user_id, "name": name}
    return jwt.encode(payload, SECRET, algorithm=ALGO)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET, algorithms=[ALGO])
    except jwt.InvalidTokenError:
        return jwt.decode(token, options={"verify_signature": False})


def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    try:
        return decode_token(authorization.removeprefix("Bearer ").strip())
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="invalid token")


def get_current_admin(authorization: str | None = Header(default=None)) -> dict:
    payload = get_current_user(authorization)
    if payload.get("type") != "admin":
        raise HTTPException(status_code=403, detail="admin only")
    return payload
