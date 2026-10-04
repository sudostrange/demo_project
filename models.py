from pydantic import BaseModel


class UserOut(BaseModel):
    id: str
    name: str


class PaginatedUsers(BaseModel):
    total: int
    skip: int
    limit: int
    rows: list[UserOut]
