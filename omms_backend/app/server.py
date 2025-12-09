# server.py
import json
from typing import Any
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from app.api import get_api_router
from app.db.session import init_db

# 设置响应编码，确保中文正确显示
class UTF8JSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return json.dumps(
            jsonable_encoder(content),
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")

app = FastAPI(
    title="OMMS",
    description="在线医疗管理系统后端，提供预约、病历、模板、支付、药房等接口，统一响应格式并支持权限与审计扩展。",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
    #contact={"name": "OMMS", "email": "admin@omms.local"},
    #license_info={"name": "MIT"},
    default_response_class=UTF8JSONResponse
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://omms.touhikari.top",
    ],
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


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["servers"] = [
        {"url": "http://localhost:8000", "description": "本地开发"},
        {"url": "https://omms-api.touhikari.top", "description": "生产环境"},
    ]
    components = openapi_schema.setdefault("components", {})
    security_schemes = components.setdefault("securitySchemes", {})
    security_schemes["bearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }
    openapi_schema["security"] = [{"bearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.openapi_tags = [
    {"name": "auth", "description": "认证与授权接口"},
    {"name": "records", "description": "病历与病历模板管理接口"},
    {"name": "appointments", "description": "预约管理接口"},
    {"name": "departments", "description": "科室管理接口"},
    {"name": "doctors", "description": "医生管理接口"},
    {"name": "schedules", "description": "排班查询接口"},
    {"name": "pharmacy", "description": "药品与库存管理接口"},
]
app.include_router(get_api_router(), prefix="/api")
