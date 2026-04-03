import os
import shutil
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.items import schemas, service
from app.users.models import User

router = APIRouter(prefix="/items", tags=["Items"])


@router.post("/", response_model=schemas.ItemOut)
def create_item(
    item: schemas.ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return service.create_item(db=db, item=item, user_id=current_user.id)


@router.post("/{item_id}/image", response_model=schemas.ItemOut)
def upload_item_image(
    item_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_item = service.get_item(db, item_id)
    if not db_item or db_item.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Item not found or not authorized")

    file_extension = file.filename.split(".")[-1]
    file_name = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join("uploads", file_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    image_url = f"/uploads/{file_name}"
    updated_item = service.update_item(
        db, item_id, schemas.ItemUpdate(image_url=image_url), current_user.id
    )

    return updated_item


@router.get("/", response_model=List[schemas.ItemOut])
def read_items(
    skip: int = 0,
    limit: int = 100,
    city: Optional[str] = None,
    category: Optional[str] = None,
    transaction_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return service.get_items(
        db,
        skip=skip,
        limit=limit,
        city=city,
        category=category,
        transaction_type=transaction_type,
    )


@router.get("/{item_id}", response_model=schemas.ItemOut)
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = service.get_item(db, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@router.put("/{item_id}", response_model=schemas.ItemOut)
def update_item(
    item_id: int,
    item_update: schemas.ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_item = service.update_item(db, item_id, item_update, current_user.id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found or not authorized")
    return db_item


@router.delete("/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    success = service.delete_item(db, item_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found or not authorized")
    return {"detail": "Item deleted"}


# ---- Comments Endpoints ----


@router.get("/{item_id}/comments", response_model=List[schemas.CommentOut])
def read_comments(item_id: int, db: Session = Depends(get_db)):
    return service.get_comments(db, item_id=item_id)


@router.post("/{item_id}/comments", response_model=schemas.CommentOut)
def create_comment(
    item_id: int,
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return service.create_comment(
        db=db, comment=comment, item_id=item_id, user_id=current_user.id
    )


@router.put("/{item_id}/comments/{comment_id}", response_model=schemas.CommentOut)
def update_comment(
    item_id: int,
    comment_id: int,
    comment_update: schemas.CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_comment = service.update_comment(db, comment_id, comment_update, current_user.id)
    if db_comment is None:
        raise HTTPException(
            status_code=404, detail="Comment not found or not authorized"
        )
    return db_comment


@router.delete("/{item_id}/comments/{comment_id}")
def delete_comment(
    item_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    success = service.delete_comment(db, comment_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=404, detail="Comment not found or not authorized"
        )
    return {"detail": "Comment deleted"}
