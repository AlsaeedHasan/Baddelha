from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.items.models import Item
from app.swaps.models import Swap
from app.users.models import User

router = APIRouter(prefix="/admin", tags=["Admin"])


def check_admin(current_user: User):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required"
        )


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    check_admin(current_user)

    total_users = db.query(func.count(User.id)).scalar()
    total_items = db.query(func.count(Item.id)).scalar()
    total_swaps = db.query(func.count(Swap.id)).scalar()
    swaps_accepted = (
        db.query(func.count(Swap.id)).filter(Swap.status == "Accepted").scalar()
    )

    return {
        "total_users": total_users,
        "total_items": total_items,
        "total_swaps_requested": total_swaps,
        "total_swaps_completed": swaps_accepted,
    }


@router.put("/users/{user_id}/ban")
def ban_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_admin(current_user)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.commit()
    return {"message": f"User {user.email} banned successfully"}
