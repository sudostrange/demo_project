from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query

from auth import create_access_token
from db import count_users, get_user, init_db, list_users, search_users, verify_user
from models import LoginIn, PaginatedUsers, TokenOut, UserOut


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="sqli-demo", lifespan=lifespan)


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/user")
def read_user(user_id: str = Query("1", alias="id")):
    rows = get_user(user_id)
    return {"rows": [{"id": r[0], "name": r[1], "password": r[2]} for r in rows]}


@app.get("/users", response_model=PaginatedUsers)
def read_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    sort: str = Query("id", pattern="^(id|name)$"),
):
    rows = list_users(limit=limit, skip=skip, sort=sort)
    return {
        "total": count_users(),
        "skip": skip,
        "limit": limit,
        "rows": [{"id": r[0], "name": r[1]} for r in rows],
    }


@app.get("/users/search", response_model=list[UserOut])
def search(q: str = Query(..., min_length=1, max_length=50)):
    rows = search_users(q)
    return [{"id": r[0], "name": r[1]} for r in rows]


@app.post("/users/login", response_model=TokenOut)
def login(body: LoginIn):
    row = verify_user(body.id, body.password)
    if row is None:
        raise HTTPException(status_code=401, detail="bad credentials")
    return TokenOut(access_token=create_access_token(row[0], row[1]))
