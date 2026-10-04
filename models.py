from pydantic import BaseModel


class UserOut(BaseModel):
    id: str
    name: str


class PaginatedUsers(BaseModel):
    total: int
    skip: int
    limit: int
    rows: list[UserOut]


class LoginIn(BaseModel):
    id: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserPatch(BaseModel):
    name: str | None = None
    password: str | None = None
    is_admin: int | None = None


class UserDetail(BaseModel):
    id: str
    name: str
    is_admin: int


class OrderIn(BaseModel):
    user_id: str
    total: float


class OrderOut(BaseModel):
    id: int
    user_id: str
    total: float


class ItemOut(BaseModel):
    id: int
    sku: str
    qty: int
