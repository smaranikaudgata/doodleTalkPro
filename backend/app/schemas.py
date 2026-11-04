#API schemas(pydantic)
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

# 1. The Base Schema: Common attributes shared across multiple schemas
class UserBase(BaseModel):
    email: EmailStr # Automatically validates that the string has an @ and a domain

# 2. The Input Schema: What the Vue frontend sends when creating an account
class UserCreate(UserBase):
    password: str # The raw password (FastAPI will hash this before sending to SQLAlchemy)

# 3. The Output Schema: What FastAPI sends back to the frontend
class UserResponse(UserBase):
    id: int
    created_at: datetime

    # This tells Pydantic to read data from a SQLAlchemy model instead of a standard Python dictionary
    model_config = ConfigDict(from_attributes=True)