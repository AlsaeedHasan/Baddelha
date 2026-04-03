from sqlalchemy import UUID, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String)
    estimated_price = Column(Float, nullable=True)
    image_url = Column(String, nullable=True)
    city = Column(String, index=True, nullable=True)
    category = Column(String, index=True, nullable=True)
    transaction_type = Column(String, index=True, nullable=True)  # Swap, Sell, or Both
    owner_id = Column(UUID, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", backref="items")
    comments = relationship(
        "Comment", back_populates="item", cascade="all, delete-orphan"
    )


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    author_id = Column(UUID, ForeignKey("users.id"), nullable=False)

    item = relationship("Item", back_populates="comments")
    author = relationship("User", backref="comments")
