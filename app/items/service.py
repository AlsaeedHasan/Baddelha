from sqlalchemy.orm import Session

from app.items.models import Comment, Item
from app.items.schemas import CommentCreate, CommentUpdate, ItemCreate, ItemUpdate


def get_items(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    city: str = None,
    category: str = None,
    transaction_type: str = None,
):
    query = db.query(Item)
    if city:
        query = query.filter(Item.city.ilike(f"%{city}%"))
    if category:
        query = query.filter(Item.category.ilike(f"%{category}%"))
    if transaction_type:
        query = query.filter(Item.transaction_type.ilike(f"%{transaction_type}%"))
    return query.offset(skip).limit(limit).all()


def get_item(db: Session, item_id: int):
    return db.query(Item).filter(Item.id == item_id).first()


def create_item(db: Session, item: ItemCreate, user_id: int):
    db_item = Item(**item.model_dump(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_item(db: Session, item_id: int, item_update: ItemUpdate, user_id: int):
    db_item = get_item(db, item_id)
    if not db_item or db_item.owner_id != user_id:
        return None
    for key, value in item_update.model_dump(exclude_unset=True).items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_item(db: Session, item_id: int, user_id: int):
    db_item = get_item(db, item_id)
    if not db_item or (db_item.owner_id != user_id):
        return False
    db.delete(db_item)
    db.commit()
    return True


def get_comments(db: Session, item_id: int):
    return db.query(Comment).filter(Comment.item_id == item_id).all()


def get_comment(db: Session, comment_id: int):
    return db.query(Comment).filter(Comment.id == comment_id).first()


def create_comment(db: Session, comment: CommentCreate, item_id: int, user_id: int):
    db_comment = Comment(text=comment.text, item_id=item_id, author_id=user_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def update_comment(
    db: Session, comment_id: int, comment_update: CommentUpdate, user_id: int
):
    db_comment = get_comment(db, comment_id)
    if not db_comment or db_comment.author_id != user_id:
        return None
    db_comment.text = comment_update.text
    db.commit()
    db.refresh(db_comment)
    return db_comment


def delete_comment(db: Session, comment_id: int, user_id: int):
    db_comment = get_comment(db, comment_id)
    if not db_comment or db_comment.author_id != user_id:
        return False
    db.delete(db_comment)
    db.commit()
    return True
