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
