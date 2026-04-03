from sqlalchemy import UUID, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Swap(Base):
    __tablename__ = "swaps"

    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    responder_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    offered_item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    requested_item_id = Column(Integer, ForeignKey("items.id"), nullable=False)

    # Status can be: Pending, Accepted, Rejected
    status = Column(String, default="Pending", nullable=False)

    requester = relationship(
        "User", foreign_keys=[requester_id], backref="requested_swaps"
    )
    responder = relationship(
        "User", foreign_keys=[responder_id], backref="received_swaps"
    )
    offered_item = relationship("Item", foreign_keys=[offered_item_id])
    requested_item = relationship("Item", foreign_keys=[requested_item_id])
