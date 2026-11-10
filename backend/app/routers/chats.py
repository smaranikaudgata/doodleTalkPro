from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_async_db
import app.db.models as models
from app import schemas, auth
from app.utils.constants import ChatRole

router = APIRouter(prefix="/api/sessions", tags=["Chats"])

@router.post("/{session_id}/messages", response_model= schemas.ChatMessageResponse)
async def create_message(
    session_id: int,
    message_in: schemas.ChatMessageCreate, # Strictly validates content and role="user"
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(auth.get_current_user) # Decodes JWT to guarantee identity
):
    # 1. Authorization Check
    session = await db.execute(
        select(models.ChatSession)
        .where(models.ChatSession.id == session_id, models.ChatSession.user_id == current_user.id)
    )
    if not session.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not authorized to access this session")

    # 2. Safe Creation
    new_message = models.ChatMessage(
        session_id=session_id, # Safely taken from the URL
        role=ChatRole(message_in.role),  # Safely constrained to "user" by Pydantic
        content=message_in.content
    )

    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)

    return new_message
