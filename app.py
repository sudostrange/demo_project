from contextlib import asynccontextmanager
import os

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from auth import AuthMiddleware, create_access_token, get_current_admin
from db import count_orders, count_users, create_order, db_stats, get_order, get_order_items, get_user, init_db, init_shop, list_orders, list_user_orders, list_users, order_revenue, recent_orders, search_users, update_user, verify_user
from models import ItemOut, LoginIn, OrderIn, OrderOut, PaginatedUsers, TokenOut, UserDetail, UserOut, UserPatch


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    init_shop()
    yield


app = FastAPI(title="super dashboard", lifespan=lifespan)
app.add_middleware(AuthMiddleware)

BASE_DIR = os.path.dirname(__file__)
os.makedirs(os.path.join(BASE_DIR, "static"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "templates"), exist_ok=True)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

from admin import router as admin_router  # noqa: E402
app.include_router(admin_router)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/dashboard", status_code=302)


@app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
def dashboard_page(request: Request):
    stats = db_stats()
    ctx = {
        "active": "dashboard",
        "total_users": stats.get("users", 0),
        "db_bytes": stats.get("db_bytes", 0),
        "total_orders": count_orders(),
        "revenue": order_revenue(),
        "recent_orders": [
            {"id": r[0], "user_id": r[1], "total": r[2]} for r in recent_orders(5)
        ],
        "users_preview": [
            {"id": r[0], "name": r[1]} for r in list_users(limit=5, skip=0)
        ],
    }
    return templates.TemplateResponse(request, "dashboard.html", ctx)


@app.get("/dashboard/users", response_class=HTMLResponse, include_in_schema=False)
def dashboard_users_page(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    sort: str = Query("id", pattern="^(id|name)$"),
    q: str | None = Query(default=None, max_length=50),
):
    if q:
        rows = search_users(q)
        total = len(rows)
    else:
        rows = list_users(limit=limit, skip=skip, sort=sort)
        total = count_users()
    ctx = {
        "active": "users",
        "rows": [{"id": r[0], "name": r[1]} for r in rows],
        "total": total,
        "skip": skip,
        "limit": limit,
        "sort": sort,
        "q": q or "",
        "prev_skip": max(0, skip - limit),
        "next_skip": skip + limit,
        "has_next": (skip + limit) < total,
    }
    return templates.TemplateResponse(request, "users.html", ctx)


@app.get("/dashboard/orders", response_class=HTMLResponse, include_in_schema=False)
def dashboard_orders_page(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    rows = list_orders(limit=limit, skip=skip)
    total = count_orders()
    ctx = {
        "active": "orders",
        "rows": [{"id": r[0], "user_id": r[1], "total": r[2]} for r in rows],
        "total": total,
        "skip": skip,
        "limit": limit,
        "prev_skip": max(0, skip - limit),
        "next_skip": skip + limit,
        "has_next": (skip + limit) < total,
        "revenue": order_revenue(),
    }
    return templates.TemplateResponse(request, "orders.html", ctx)


@app.get("/dashboard/orders/{order_id}", response_class=HTMLResponse, include_in_schema=False)
def dashboard_order_detail_page(request: Request, order_id: int):
    row = get_order(order_id)
    if row is None:
        raise HTTPException(status_code=404, detail="order not found")
    ctx = {
        "active": "orders",
        "order": {"id": row[0], "user_id": row[1], "total": row[2]},
        "items": [
            {"id": r[0], "sku": r[1], "qty": r[2]} for r in get_order_items(order_id)
        ],
    }
    return templates.TemplateResponse(request, "order_detail.html", ctx)


@app.get("/dashboard/login", response_class=HTMLResponse, include_in_schema=False)
def dashboard_login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"active": "login"})


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


@app.get("/admin/whoami")
def whoami(admin: dict = Depends(get_current_admin)):
    return {"sub": admin.get("sub"), "type": admin.get("type")}


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
