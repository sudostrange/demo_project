from contextlib import asynccontextmanager
import os

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import PlainTextResponse

from auth import create_access_token
from db import count_users, create_order, db_stats, get_order, get_order_items, get_user, init_db, init_shop, list_user_orders, list_users, search_users, update_user, verify_user
from models import ItemOut, LoginIn, OrderIn, OrderOut, PaginatedUsers, TokenOut, UserDetail, UserOut, UserPatch


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    init_shop()
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


@app.patch("/users/{user_id}", response_model=UserDetail)
def patch_user(user_id: str, body: UserPatch):
    row = update_user(user_id, body.model_dump(exclude_none=True))
    if row is None:
        raise HTTPException(status_code=404, detail="no updatable fields or user not found")
    return {"id": row[0], "name": row[1], "is_admin": row[2]}


@app.get("/admin/stats")
def stats():
    return db_stats()


@app.get("/admin/export", response_class=PlainTextResponse)
def export(file: str = Query("users.csv", max_length=100)):
    path = os.path.join("exports", file)
    with open(path) as fh:
        return fh.read()


@app.post("/orders", response_model=OrderOut)
def place_order(body: OrderIn):
    oid = create_order(body.user_id, body.total)
    return {"id": oid, "user_id": body.user_id, "total": body.total}


@app.get("/orders/{order_id}", response_model=OrderOut)
def order_detail(order_id: int):
    row = get_order(order_id)
    if row is None:
        raise HTTPException(status_code=404, detail="order not found")
    return {"id": row[0], "user_id": row[1], "total": row[2]}


@app.get("/orders/{order_id}/items", response_model=list[ItemOut])
def order_items(order_id: int):
    if get_order(order_id) is None:
        raise HTTPException(status_code=404, detail="order not found")
    return [{"id": r[0], "sku": r[1], "qty": r[2]} for r in get_order_items(order_id)]


@app.get("/users/{user_id}/orders", response_model=list[OrderOut])
def user_orders(user_id: str):
    return [{"id": r[0], "user_id": r[1], "total": r[2]} for r in list_user_orders(user_id)]
