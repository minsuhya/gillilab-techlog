from pydantic import BaseModel, EmailStr
from typing import Optional, List

class TokenData(BaseModel):
    username: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class UserBase(BaseModel):
    email: EmailStr
    username: str
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    role: str = "user"

class UserInDB(User):
    hashed_password: str 