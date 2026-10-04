from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from db import set_superadmin

router = APIRouter()


class PromoteIn(BaseModel):
    id: str


@router.post("/admin/promote", deprecated=True)
def promote(body: PromoteIn):
    row = set_superadmin(body.id)
    if row is None:
        raise HTTPException(status_code=404, detail="user not found")
    return {"id": row[0], "name": row[1], "is_admin": row[2]}
