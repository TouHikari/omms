# server.py
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.middleware.cors import CORSMiddleware
from app.api import get_api_router
from app.db.session import init_db

app = FastAPI(
    title="OMMS",
    description="在线医疗管理系统后端，提供预约、病历、模板、支付、药房等接口，统一响应格式并支持权限与审计扩展。",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
    contact={"name": "OMMS", "email": "admin@omms.local"},
    license_info={"name": "MIT"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.get("/health")
async def health():
    return {"code": 200, "message": "success", "data": "ok"}

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="OMMS",
        swagger_js_url="https://cdn.staticfile.org/swagger-ui/5.11.2/swagger-ui-bundle.min.js",
        swagger_css_url="https://cdn.staticfile.org/swagger-ui/5.11.2/swagger-ui.css",
    )

app.openapi_tags = [
    {"name": "records", "description": "病历与病历模板管理接口"},
]
app.include_router(get_api_router(), prefix="/api")
