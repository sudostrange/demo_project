from contextlib import asynccontextmanager

from fastapi import FastAPI, Query

from db import get_user, init_db


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
