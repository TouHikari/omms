# server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.records_api import router as records_router, init_models

app = FastAPI(title="OMMS Records API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    await init_models()

@app.get("/health")
async def health():
    return {"code": 200, "message": "success", "data": "ok"}

app.include_router(records_router, prefix="/api")