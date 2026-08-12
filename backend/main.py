# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.auth_router import router as auth_router
from app.routers.document_router import router as document_router
from app.routers.search_router import router as search_router

app = FastAPI(title="Student Assistant")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router)
app.include_router(document_router)
app.include_router(search_router)


@app.get("/")
def root():
    return {"message": "Server running successfully"}


@app.get("/health")
def health():
    return {"status": "healthy"}