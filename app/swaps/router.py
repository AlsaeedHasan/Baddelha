from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.swaps import schemas, service
from app.users.models import User

router = APIRouter(prefix="/swaps", tags=["Swaps"])


@router.post("/request", response_model=schemas.SwapOut)
def request_swap(
    swap: schemas.SwapCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_swap = service.create_swap_request(db, swap, current_user.id)
    if not db_swap:
        raise HTTPException(status_code=400, detail="Invalid request. Check item IDs.")
    return db_swap


@router.put("/{swap_id}/accept", response_model=schemas.SwapOut)
def accept_swap(
    swap_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_swap = service.update_swap_status(db, swap_id, current_user.id, "Accepted")
    if not db_swap:
        raise HTTPException(status_code=404, detail="Swap not found or unauthorized")
    return db_swap


@router.put("/{swap_id}/reject", response_model=schemas.SwapOut)
def reject_swap(
    swap_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_swap = service.update_swap_status(db, swap_id, current_user.id, "Rejected")
    if not db_swap:
        raise HTTPException(status_code=404, detail="Swap not found or unauthorized")
    return db_swap


@router.get("/my-requests", response_model=List[schemas.SwapOut])
def my_swaps(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    return service.get_my_swaps(db, current_user.id)
