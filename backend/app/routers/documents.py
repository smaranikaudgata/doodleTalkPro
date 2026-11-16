import os
import re
import gc
import uuid
import asyncio
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select

from app.db.session import get_async_db
import app.db.models as models
from app import schemas
from app import auth
from app.utils.constants import DocumentStatus
from app.utils.document_parser import extract_text

router = APIRouter(prefix="/api/documents", tags=["Documents"])

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}

os.makedirs(UPLOAD_DIR, exist_ok=True)


# Strips directory traversal paths and unsafe characters
def _secure_filename(filename: str) -> str:
    basename = os.path.basename(filename)
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', basename)


# Verifies the binary file signature matches the claimed extension
def _validate_magic_bytes(header: bytes, ext: str) -> bool:
    if ext == ".pdf":
        return header.startswith(b"%PDF-")
    elif ext == ".docx":
        return header.startswith(b"PK\x03\x04")
    elif ext == ".txt":
        return b"\x00" not in header
    return False


# Deletes staged file with exponential backoff to bypass transient Windows file locks
async def _cleanup_file_with_retry(file_path: str, retries: int = 3, delay: float = 0.5) -> bool:
    for attempt in range(1, retries + 1):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except OSError as e:
            if attempt == retries:
                print(f"[CRITICAL] Failed to delete {file_path} after {retries} attempts: {e}")
                return False
            gc.collect()
            await asyncio.sleep(delay * (2 ** (attempt - 1)))
    return False


# Offloads CPU-heavy text extraction to a worker thread, updates PostgreSQL, and guarantees ephemeral file cleanup
async def _process_document_background(document_id: int, file_path: str):
    final_status = DocumentStatus.failed

    try:
        raw_text = await asyncio.to_thread(extract_text, file_path)

        if raw_text.strip():
            final_status = DocumentStatus.completed

    except Exception as e:
        print(f"Background Processing Error for doc {document_id}: {e}")

    finally:
        # Update PostgreSQL once
        async for db in get_async_db():
            await db.execute(
                update(models.Document)
                .where(models.Document.id == document_id)
                .values(status=final_status)
            )
            await db.commit()
            break
            
        # Cleanup
        await _cleanup_file_with_retry(file_path)


@router.post("/", response_model=schemas.DocumentResponse)
async def upload_document(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File is too large. Maximum allowed size is {MAX_FILE_SIZE / (1024 * 1024)} MB."
        )
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is missing")
        
    safe_display_name = _secure_filename(file.filename)
    file_ext = os.path.splitext(safe_display_name)[1].lower()

    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Supported formats: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    header = await file.read(8)
    if not _validate_magic_bytes(header, file_ext):
        raise HTTPException(
            status_code=400,
            detail=f"File content does not match extension '{file_ext}'"
        )
    await file.seek(0)

    user_dir = os.path.join(UPLOAD_DIR, str(current_user.id))
    os.makedirs(user_dir, exist_ok=True)
    
    unique_disk_name = f"{uuid.uuid4().hex[:8]}_{safe_display_name}"
    file_path = os.path.join(user_dir, unique_disk_name)

    total_bytes = 0
    try:
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                total_bytes += len(chunk)
                if total_bytes > MAX_FILE_SIZE:
                    buffer.close()
                    os.remove(file_path)
                    raise HTTPException(status_code=413, detail="File exceeds 10MB limit")
                buffer.write(chunk)
    except HTTPException:
        raise
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    new_doc = models.Document(
        user_id=current_user.id,
        filename=safe_display_name,
        file_path=file_path,
        status=DocumentStatus.processing 
    )

    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)

    background_tasks.add_task(_process_document_background, new_doc.id, file_path)

    return new_doc


@router.get("/", response_model=list[schemas.DocumentResponse])
async def get_user_documents(
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    result = await db.execute(
        select(models.Document)
        .where(models.Document.user_id == current_user.id)
        .order_by(models.Document.created_at.desc())
    )
    return result.scalars().all()


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    result = await db.execute(
        select(models.Document)
        .where(
            models.Document.id == document_id,
            models.Document.user_id == current_user.id
        )
    )
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    await db.delete(doc)
    await db.commit()
    return None