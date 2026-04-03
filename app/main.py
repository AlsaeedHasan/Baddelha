import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.admin.router import router as admin_router
from app.chat.router import router as chat_router
from app.core.config import settings
from app.items.router import router as items_router
from app.swaps.router import router as swaps_router
from app.users.router import router as users_router

app = FastAPI(title=settings.PROJECT_NAME)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(users_router)
app.include_router(items_router)
app.include_router(swaps_router)
app.include_router(chat_router)
app.include_router(admin_router)


@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}
