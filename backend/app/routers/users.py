from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_db
import db.models as models
import schemas
import auth

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_async_db)):
    # 1. Hash the plaintext password provided by the frontend
    hashed_pw = auth.hash_password(user.password)

    # 2. Explicitly map the fields to the SQLAlchemy model
    # Do not use **user.model_dump() because Pydantic provides 'password' but SQLAlchemy expects 'hashed_password'
    new_user = models.User(
        email=user.email,
        hashed_password=hashed_pw 
    )
    
    # 3. Async transaction sequence to save the row and fetch the auto-generated Postgres ID
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # The response_model automatically filters out the hashed password before sending JSON
    return new_user

@router.get("/me", response_model=schemas.UserResponse)
async def get_my_profile(current_user: models.User = Depends(auth.get_current_user)):
    # current_user is already fully validated and fetched from the DB by the dependency (app/auth.py)
    return current_user