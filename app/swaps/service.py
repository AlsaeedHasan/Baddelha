from sqlalchemy.orm import Session

from app.chat.models import ChatRoom
from app.items.models import Item
from app.swaps.models import Swap
from app.swaps.schemas import SwapCreate


def create_swap_request(db: Session, swap: SwapCreate, user_id: int):
    # Fetch requested item to get the responder id
    requested_item = db.query(Item).filter(Item.id == swap.requested_item_id).first()
    if not requested_item:
        return None

    db_swap = Swap(
        requester_id=user_id,
        responder_id=requested_item.owner_id,
        offered_item_id=swap.offered_item_id,
        requested_item_id=swap.requested_item_id,
        status="Pending",
    )
    db.add(db_swap)
    db.commit()
    db.refresh(db_swap)
    return db_swap


def update_swap_status(db: Session, swap_id: int, user_id: int, status: str):
    db_swap = db.query(Swap).filter(Swap.id == swap_id).first()
    if not db_swap:
        return None

    # Only responder can accept or reject
    if db_swap.responder_id != user_id:
        return None

    db_swap.status = status
    db.commit()
    db.refresh(db_swap)

    # If accepted, trigger chat room creation
    if status == "Accepted":
        existing_chat = db.query(ChatRoom).filter(ChatRoom.swap_id == swap_id).first()
        if not existing_chat:
            chat_room = ChatRoom(swap_id=swap_id)
            db.add(chat_room)
            db.commit()

    return db_swap


def get_my_swaps(db: Session, user_id: int):
    return (
        db.query(Swap)
        .filter((Swap.requester_id == user_id) | (Swap.responder_id == user_id))
        .all()
    )
