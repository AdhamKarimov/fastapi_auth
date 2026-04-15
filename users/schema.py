from pydantic import BaseModel
from typing import Optional


class SignUp(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    username: str
    email: str
    password: str


class Login(BaseModel):
    username_or_email: str
    password: str
