# records_api.py
import os
import json
import random
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import String, Integer, Text, select, func
from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.settings import settings

engine = create_async_engine(settings.database_url, pool_pre_ping=True, echo=False, future=True, connect_args=settings.connect_args())
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

def ok(data=None, message="success"):
    return {"code": 200, "message": message, "data": data}

def err(code: int, message: str):
    return {"code": code, "message": message}

def gen_record_id(date_str: str):
    return f"MR-{date_str.replace('-', '')}-{str(random.randint(0, 9999)).zfill(4)}"

def now_date_str():
    return datetime.now().strftime("%Y-%m-%d")

def compose_time(date_str: str, hhmm: Optional[str]):
    return f"{date_str} {hhmm or '10:00'}"

def to_list(text_val: Optional[str]) -> List[str]:
    if not text_val:
        return []
    try:
        val = json.loads(text_val)
        return val if isinstance(val, list) else []
    except Exception:
        return []

def to_json_str(val: Optional[List[str]]) -> Optional[str]:
    if not val:
        return None
    return json.dumps([v for v in val if isinstance(v, str) and v.strip()], ensure_ascii=False)

class MedicalRecord(Base):
    __tablename__ = "records"
    id: Mapped[str] = mapped_column(String(24), primary_key=True)
    dept_id: Mapped[int] = mapped_column(Integer, index=True)
    doctor_id: Mapped[int] = mapped_column(Integer, index=True)
    patient_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    patient_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    created_at: Mapped[str] = mapped_column(String(19), index=True)
    status: Mapped[str] = mapped_column(String(20), index=True, default="draft")
    template_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    chief_complaint: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    diagnosis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prescriptions_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    labs_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    imaging_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

class RecordTemplate(Base):
    __tablename__ = "record_templates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    scope: Mapped[str] = mapped_column(String(50), index=True)
    fields_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    defaults_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

class RecordCreate(BaseModel):
    deptId: int
    doctorId: int
    patientId: Optional[int] = None
    patientName: Optional[str] = None
    time: Optional[str] = None
    chiefComplaint: Optional[str] = None
    diagnosis: Optional[str] = None
    prescriptions: Optional[List[str]] = None
    labs: Optional[List[str]] = None
    imaging: Optional[List[str]] = None
    templateId: Optional[int] = None

class RecordUpdate(BaseModel):
    patientId: Optional[int] = None
    patientName: Optional[str] = None
    chiefComplaint: Optional[str] = None
    diagnosis: Optional[str] = None
    prescriptions: Optional[List[str]] = None
    labs: Optional[List[str]] = None
    imaging: Optional[List[str]] = None
    createdAt: Optional[str] = None
    deptId: Optional[int] = None
    doctorId: Optional[int] = None

class TemplateCreate(BaseModel):
    name: str
    scope: Optional[str] = "通用"
    fields: Optional[List[str]] = None
    defaults: Optional[dict] = None

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    scope: Optional[str] = None
    fields: Optional[List[str]] = None
    defaults: Optional[dict] = None

router = APIRouter(tags=["records"])

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@router.get("/records")
async def list_records(
    status: Optional[str] = Query(default=None),
    date: Optional[str] = Query(default=None),
    deptId: Optional[int] = Query(default=None),
    doctorId: Optional[int] = Query(default=None),
    hasLab: Optional[bool] = Query(default=None),
    hasImaging: Optional[bool] = Query(default=None),
    page: int = Query(default=1),
    pageSize: int = Query(default=20),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(MedicalRecord)
    if status:
        stmt = stmt.where(MedicalRecord.status == status)
    if date:
        stmt = stmt.where(MedicalRecord.created_at.like(f"{date}%"))
    if deptId:
        stmt = stmt.where(MedicalRecord.dept_id == deptId)
    if doctorId:
        stmt = stmt.where(MedicalRecord.doctor_id == doctorId)
    total_res = await session.execute(select(func.count()).select_from(stmt.subquery()))
    total_db = int(total_res.scalar_one())
    res = await session.execute(stmt.order_by(MedicalRecord.created_at.desc()))
    all_items = []
    for r in res.scalars().all():
        prescriptions = to_list(r.prescriptions_json)
        labs = to_list(r.labs_json)
        imaging = to_list(r.imaging_json)
        item = {
            "id": r.id,
            "patient": r.patient_name or "",
            "department": str(r.dept_id),
            "doctor": str(r.doctor_id),
            "createdAt": r.created_at,
            "status": r.status,
            "hasLab": len(labs) > 0,
            "hasImaging": len(imaging) > 0,
            "chiefComplaint": r.chief_complaint or "",
            "diagnosis": r.diagnosis or "",
            "prescriptions": prescriptions,
            "labs": labs,
            "imaging": imaging,
        }
        all_items.append(item)
    if hasLab is not None:
        all_items = [x for x in all_items if x["hasLab"] == hasLab]
    if hasImaging is not None:
        all_items = [x for x in all_items if x["hasImaging"] == hasImaging]
    total = len(all_items)
    start = max(0, (page - 1) * pageSize)
    end = start + pageSize
    return ok({"list": all_items[start:end], "total": total, "page": page, "pageSize": pageSize})

@router.get("/records/{id}")
async def get_record(id: str, session: AsyncSession = Depends(get_session)):
    r = await session.get(MedicalRecord, id)
    if not r:
        return err(404, "Record not found")
    prescriptions = to_list(r.prescriptions_json)
    labs = to_list(r.labs_json)
    imaging = to_list(r.imaging_json)
    return ok({
        "id": r.id,
        "patient": r.patient_name or "",
        "department": str(r.dept_id),
        "doctor": str(r.doctor_id),
        "createdAt": r.created_at,
        "status": r.status,
        "hasLab": len(labs) > 0,
        "hasImaging": len(imaging) > 0,
        "chiefComplaint": r.chief_complaint or "",
        "diagnosis": r.diagnosis or "",
        "prescriptions": prescriptions,
        "labs": labs,
        "imaging": imaging,
    })

@router.post("/records")
async def create_record(payload: RecordCreate, session: AsyncSession = Depends(get_session)):
    if not payload.deptId or not payload.doctorId:
        return err(400, "缺少deptId或doctorId")
    date_str = now_date_str()
    rid = gen_record_id(date_str)
    created_at = compose_time(date_str, payload.time)
    try:
        ca_dt = datetime.strptime(created_at, "%Y-%m-%d %H:%M")
        if ca_dt > datetime.now():
            return err(400, "createdAt不可晚于当前时间")
    except Exception:
        return err(400, "时间格式非法")
    rec = MedicalRecord(
        id=rid,
        dept_id=payload.deptId,
        doctor_id=payload.doctorId,
        patient_id=payload.patientId,
        patient_name=(payload.patientName or "").strip() or None,
        created_at=created_at,
        status="draft",
        template_id=payload.templateId,
        chief_complaint=payload.chiefComplaint or "",
        diagnosis=payload.diagnosis or "",
        prescriptions_json=to_json_str(payload.prescriptions),
        labs_json=to_json_str(payload.labs),
        imaging_json=to_json_str(payload.imaging),
    )
    session.add(rec)
    await session.commit()
    labs = to_list(rec.labs_json)
    imaging = to_list(rec.imaging_json)
    return ok({
        "id": rec.id,
        "patient": rec.patient_name or "",
        "department": str(rec.dept_id),
        "doctor": str(rec.doctor_id),
        "createdAt": rec.created_at,
        "status": rec.status,
        "hasLab": len(labs) > 0,
        "hasImaging": len(imaging) > 0,
        "chiefComplaint": rec.chief_complaint or "",
        "diagnosis": rec.diagnosis or "",
        "prescriptions": to_list(rec.prescriptions_json),
        "labs": labs,
        "imaging": imaging,
    }, "病历创建成功")

@router.put("/records/{id}")
async def update_record(id: str, payload: RecordUpdate, session: AsyncSession = Depends(get_session)):
    rec = await session.get(MedicalRecord, id)
    if not rec:
        return err(404, "Record not found")
    if payload.patientId is not None:
        rec.patient_id = payload.patientId
    if payload.patientName is not None:
        rec.patient_name = (payload.patientName or "").strip() or rec.patient_name
    if payload.chiefComplaint is not None:
        rec.chief_complaint = payload.chiefComplaint or ""
    if payload.diagnosis is not None:
        rec.diagnosis = payload.diagnosis or ""
    if payload.prescriptions is not None:
        rec.prescriptions_json = to_json_str(payload.prescriptions)
    if payload.labs is not None:
        rec.labs_json = to_json_str(payload.labs)
    if payload.imaging is not None:
        rec.imaging_json = to_json_str(payload.imaging)
    if payload.createdAt is not None:
        try:
            ca_dt = datetime.strptime(payload.createdAt, "%Y-%m-%d %H:%M")
            if ca_dt > datetime.now():
                return err(400, "createdAt不可晚于当前时间")
            rec.created_at = payload.createdAt
        except Exception:
            return err(400, "时间格式非法")
    if payload.deptId is not None:
        rec.dept_id = payload.deptId
    if payload.doctorId is not None:
        rec.doctor_id = payload.doctorId
    await session.commit()
    prescriptions = to_list(rec.prescriptions_json)
    labs = to_list(rec.labs_json)
    imaging = to_list(rec.imaging_json)
    return ok({
        "id": rec.id,
        "patient": rec.patient_name or "",
        "department": str(rec.dept_id),
        "doctor": str(rec.doctor_id),
        "createdAt": rec.created_at,
        "status": rec.status,
        "hasLab": len(labs) > 0,
        "hasImaging": len(imaging) > 0,
        "chiefComplaint": rec.chief_complaint or "",
        "diagnosis": rec.diagnosis or "",
        "prescriptions": prescriptions,
        "labs": labs,
        "imaging": imaging,
    })

@router.patch("/records/{id}/status")
async def update_record_status(id: str, payload: dict, session: AsyncSession = Depends(get_session)):
    status = (payload.get("status") or "").strip()
    if status not in ("draft", "finalized", "cancelled"):
        return err(400, "非法状态值")
    rec = await session.get(MedicalRecord, id)
    if not rec:
        return err(404, "Record not found")
    if rec.status in ("finalized", "cancelled") and status == "draft":
        return err(400, "状态不可回退")
    if status == "finalized":
        if not (rec.chief_complaint or rec.diagnosis):
            return err(400, "最终签署前至少填写主诉或诊断")
    rec.status = status
    await session.commit()
    return ok({"id": rec.id, "status": rec.status})

@router.delete("/records/{id}")
async def delete_record(id: str, session: AsyncSession = Depends(get_session)):
    rec = await session.get(MedicalRecord, id)
    if not rec:
        return err(404, "Record not found")
    rec.status = "cancelled"
    await session.commit()
    return ok({"id": rec.id, "status": rec.status})

@router.get("/record-templates")
async def get_record_templates(session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(RecordTemplate).order_by(RecordTemplate.id.desc()))
    items = []
    for t in res.scalars().all():
        items.append({
            "id": t.id,
            "name": t.name,
            "scope": t.scope,
            "fields": to_list(t.fields_json),
            "defaults": json.loads(t.defaults_json or "{}"),
        })
    return ok(items)

@router.get("/record-templates/{tpl_id}")
async def get_record_template_by_id(tpl_id: int, session: AsyncSession = Depends(get_session)):
    tpl = await session.get(RecordTemplate, tpl_id)
    if not tpl:
        return err(404, "Template not found")
    return ok({
        "id": tpl.id,
        "name": tpl.name,
        "scope": tpl.scope,
        "fields": to_list(tpl.fields_json),
        "defaults": json.loads(t.defaults_json or "{}"),
    })

@router.post("/record-templates")
async def create_record_template(payload: TemplateCreate, session: AsyncSession = Depends(get_session)):
    tpl = RecordTemplate(
        name=(payload.name or "").strip() or "未命名模板",
        scope=(payload.scope or "").strip() or "通用",
        fields_json=to_json_str(payload.fields),
        defaults_json=json.dumps(payload.defaults or {
            "chiefComplaint": "",
            "diagnosis": "",
            "prescriptions": [],
            "labs": [],
            "imaging": [],
        }, ensure_ascii=False),
    )
    session.add(tpl)
    await session.commit()
    await session.refresh(tpl)
    return ok({
        "id": tpl.id,
        "name": tpl.name,
        "scope": tpl.scope,
        "fields": to_list(tpl.fields_json),
        "defaults": json.loads(tpl.defaults_json or "{}"),
    }, "模板创建成功")

@router.put("/record-templates/{tpl_id}")
async def update_record_template(tpl_id: int, payload: TemplateUpdate, session: AsyncSession = Depends(get_session)):
    tpl = await session.get(RecordTemplate, tpl_id)
    if not tpl:
        return err(404, "Template not found")
    if payload.name is not None:
        tpl.name = (payload.name or "").strip() or tpl.name
    if payload.scope is not None:
        tpl.scope = (payload.scope or "").strip() or tpl.scope
    if payload.fields is not None:
        tpl.fields_json = to_json_str(payload.fields)
    if payload.defaults is not None:
        tpl.defaults_json = json.dumps(payload.defaults or {}, ensure_ascii=False)
    await session.commit()
    return ok({
        "id": tpl.id,
        "name": tpl.name,
        "scope": tpl.scope,
        "fields": to_list(tpl.fields_json),
        "defaults": json.loads(tpl.defaults_json or "{}"),
    }, "模板更新成功")

@router.delete("/record-templates/{tpl_id}")
async def delete_record_template(tpl_id: int, session: AsyncSession = Depends(get_session)):
    in_use_res = await session.execute(select(func.count()).select_from(MedicalRecord).where(MedicalRecord.template_id == tpl_id))
    if int(in_use_res.scalar_one()) > 0:
        return err(409, "模板被引用，无法删除")
    tpl = await session.get(RecordTemplate, tpl_id)
    if not tpl:
        return err(404, "Template not found")
    await session.delete(tpl)
    await session.commit()
    return ok({"id": tpl_id}, "模板删除成功")