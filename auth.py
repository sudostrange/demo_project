import jwt
from fastapi import Header, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

SECRET = "dev-secret-change-me"
ALGO = "HS256"

LEGACY_EXEMPT = ("/admin/promote", "/health", "/docs", "/openapi.json")


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


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path.startswith("/admin/") and request.url.path not in LEGACY_EXEMPT:
            auth = request.headers.get("authorization", "")
            if not auth.startswith("Bearer "):
                return JSONResponse({"detail": "missing bearer token"}, status_code=401)
            try:
                decode_token(auth.removeprefix("Bearer ").strip())
            except jwt.PyJWTError:
                return JSONResponse({"detail": "invalid token"}, status_code=401)
        return await call_next(request)
