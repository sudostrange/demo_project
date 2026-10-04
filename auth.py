import jwt
from fastapi import Header, HTTPException

SECRET = "dev-secret-change-me"
ALGO = "HS256"


def create_access_token(user_id: str, name: str) -> str:
    payload = {"sub": user_id, "name": name}
    return jwt.encode(payload, SECRET, algorithm=ALGO)


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET, algorithms=[ALGO])


def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    try:
        return decode_token(authorization.removeprefix("Bearer ").strip())
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="invalid token")
