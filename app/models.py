from pydantic import BaseModel
from typing import Optional

class QueryBody(BaseModel):
    query: str

class CookieRecord(BaseModel):
    id: Optional[int] = None
    domain: str
    cookie: str
    user: str

class CookieUpdate(BaseModel):
    cookie: str 