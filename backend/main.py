# main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import all models to register them with Base (must be before creating routers)
from app.models.user import User
from app.models.document import Document
from app.models.chunk import DocumentChunk
from app.models.conversation import Conversation
from app.models.message import Message

from app.routers.auth_router import router as auth_router
from app.routers.document_router import router as document_router
from app.routers.search_router import router as search_router
from app.routers.chat_router import router as chat_router

app = FastAPI(title="Student Assistant")

# CORS Configuration - read from environment
allowed_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include Routers
app.include_router(auth_router)
app.include_router(document_router)
app.include_router(search_router)
app.include_router(chat_router)


@app.get("/")
def root():
    return {"message": "Server running successfully"}


@app.get("/health")
def health():
    return {"status": "healthy"}
