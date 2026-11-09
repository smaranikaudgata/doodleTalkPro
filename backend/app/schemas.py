#API schemas(pydantic)
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime

# 1. The Base Schema: Common attributes shared across multiple schemas
class UserBase(BaseModel):
    email: EmailStr # Automatically validates that the string has an @ and a domain

# 2. The Input Schema: What the Vue frontend sends when creating an account
class UserCreate(UserBase):
    password: str = Field(min_length=8) # The raw password (FastAPI will hash this before sending to SQLAlchemy)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# 3. The Output Schema: What FastAPI sends back to the frontend
class UserResponse(UserBase):
    id: int
    created_at: datetime

    # This tells Pydantic to read data from a SQLAlchemy model instead of a standard Python dictionary
    model_config = ConfigDict(from_attributes=True)