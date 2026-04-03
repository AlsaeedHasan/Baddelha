import logging
import os
import sys

from sqlalchemy.orm import Session

# Add the parent directory to sys.path to ensure modules are found
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.users.models import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_admin(db: Session) -> None:
    admin_email = settings.ADMIN_EMAIL
    admin_password = settings.ADMIN_PASSWORD

    user = db.query(User).filter(User.email == admin_email).first()
    if not user:
        logger.info(f"Admin user {admin_email} not found. Creating...")
        hashed_password = get_password_hash(admin_password)
        admin_user = User(
            email=admin_email,
            hashed_password=hashed_password,
            full_name="Admin User",
            is_active=True,
            is_admin=True,
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        logger.info(f"Admin user created successfully with ID: {admin_user.id}")
    else:
        logger.info(f"Admin user {admin_email} already exists. Skipping creation.")


def main() -> None:
    logger.info("Starting database seeding...")
    db = SessionLocal()
    try:
        seed_admin(db)
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
    finally:
        db.close()
    logger.info("Database seeding finished.")


if __name__ == "__main__":
    main()
