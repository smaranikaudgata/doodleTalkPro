from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.session import get_async_db
import db.models as models
import schemas
import auth

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/login", response_model=schemas.Token)
async def login(
    user_credentials: schemas.UserLogin, 
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(models.User).where(models.User.email == user_credentials.email)
    )
    user = result.scalar_one_or_none()

    # Use a generic error to prevent email enumeration attacks
    if not user or not auth.verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Invalid Credentials"
        )
    
    # Mint JWT using the database ID as the subject ("sub")
    access_token = auth.create_access_token(data={"sub": str(user.id)})
    
    return {"access_token": access_token, "token_type": "bearer"}