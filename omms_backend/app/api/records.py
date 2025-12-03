import json
import random
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response import err, ok
from app.db.session import get_session
from app.models.record import MedicalRecord, RecordTemplate
from app.schemas.record import (
    RecordCreate,
    RecordUpdate,
    TemplateCreate,
    TemplateUpdate,
    MedicalRecordOut,
    RecordsListResponse,
    RecordResponse,
    RecordStatusResponse,
    DeleteRecordResponse,
    RecordTemplateOut,
    RecordTemplateListResponse,
    RecordTemplateResponse,
    TemplateDeleteResponse,
)


router = APIRouter(tags=["records"])


def gen_record_id(date_str: str) -> str:
    return f"MR-{date_str.replace('-', '')}-{str(random.randint(0, 9999)).zfill(4)}"


def now_date_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def compose_time(date_str: str, hhmm: Optional[str]) -> str:
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


@router.get(
    "/records",
    summary="病历列表查询",
    description="按状态、日期、科室、医生筛选病历列表，支持分页与检验/影像过滤。",
    response_model=RecordsListResponse,
)
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


@router.get(
    "/records/{id}",
    summary="病历详情",
    description="按病历号获取病历详情。",
    response_model=RecordResponse,
)
async def get_record(id: str, session: AsyncSession = Depends(get_session)):
    r = await session.get(MedicalRecord, id)
    if not r:
        return err(404, "Record not found")
    prescriptions = to_list(r.prescriptions_json)
    labs = to_list(r.labs_json)
    imaging = to_list(r.imaging_json)
    return ok(
        {
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
    )


@router.post(
    "/records",
    summary="创建病历",
    description="生成病历号并创建草稿病历，校验时间与必填项。",
    response_model=RecordResponse,
)
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
    return ok(
        {
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
        },
        "病历创建成功",
    )


@router.put(
    "/records/{id}",
    summary="更新病历",
    description="更新病历内容，支持主诉、诊断、处方、检验、影像、基本信息等。",
    response_model=RecordResponse,
)
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
    return ok(
        {
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
        }
    )


@router.patch(
    "/records/{id}/status",
    summary="更新病历状态",
    description="合法状态为 draft|finalized|cancelled，终稿前需至少填写主诉或诊断，已终稿/作废不可回退。",
    response_model=RecordStatusResponse,
)
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


@router.delete(
    "/records/{id}",
    summary="作废病历",
    description="将病历状态置为 cancelled。",
    response_model=DeleteRecordResponse,
)
async def delete_record(id: str, session: AsyncSession = Depends(get_session)):
    rec = await session.get(MedicalRecord, id)
    if not rec:
        return err(404, "Record not found")
    rec.status = "cancelled"
    await session.commit()
    return ok({"id": rec.id, "status": rec.status})


@router.get(
    "/record-templates",
    summary="模板列表",
    description="查询病历模板列表。",
    response_model=RecordTemplateListResponse,
)
async def get_record_templates(session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(RecordTemplate).order_by(RecordTemplate.id.desc()))
    items = []
    for t in res.scalars().all():
        items.append(
            {
                "id": t.id,
                "name": t.name,
                "scope": t.scope,
                "fields": to_list(t.fields_json),
                "defaults": json.loads(t.defaults_json or "{}"),
            }
        )
    return ok(items)


@router.get(
    "/record-templates/{tpl_id}",
    summary="模板详情",
    description="按ID查询模板详情。",
    response_model=RecordTemplateResponse,
)
async def get_record_template_by_id(tpl_id: int, session: AsyncSession = Depends(get_session)):
    tpl = await session.get(RecordTemplate, tpl_id)
    if not tpl:
        return err(404, "Template not found")
    return ok(
        {
            "id": tpl.id,
            "name": tpl.name,
            "scope": tpl.scope,
            "fields": to_list(tpl.fields_json),
            "defaults": json.loads(tpl.defaults_json or "{}"),
        }
    )


@router.post(
    "/record-templates",
    summary="创建模板",
    description="创建病历模板，并可设置默认字段。",
    response_model=RecordTemplateResponse,
)
async def create_record_template(payload: TemplateCreate, session: AsyncSession = Depends(get_session)):
    tpl = RecordTemplate(
        name=(payload.name or "").strip() or "未命名模板",
        scope=(payload.scope or "").strip() or "通用",
        fields_json=to_json_str(payload.fields),
        defaults_json=json.dumps(
            payload.defaults
            or {
                "chiefComplaint": "",
                "diagnosis": "",
                "prescriptions": [],
                "labs": [],
                "imaging": [],
            },
            ensure_ascii=False,
        ),
    )
    session.add(tpl)
    await session.commit()
    await session.refresh(tpl)
    return ok(
        {
            "id": tpl.id,
            "name": tpl.name,
            "scope": tpl.scope,
            "fields": to_list(tpl.fields_json),
            "defaults": json.loads(tpl.defaults_json or "{}"),
        },
        "模板创建成功",
    )


@router.put(
    "/record-templates/{tpl_id}",
    summary="更新模板",
    description="更新模板的名称、范围、字段与默认值。",
    response_model=RecordTemplateResponse,
)
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
    return ok(
        {
            "id": tpl.id,
            "name": tpl.name,
            "scope": tpl.scope,
            "fields": to_list(tpl.fields_json),
            "defaults": json.loads(tpl.defaults_json or "{}"),
        },
        "模板更新成功",
    )


@router.delete(
    "/record-templates/{tpl_id}",
    summary="删除模板",
    description="模板被引用时返回 409。",
    response_model=TemplateDeleteResponse,
)
async def delete_record_template(tpl_id: int, session: AsyncSession = Depends(get_session)):
    in_use_res = await session.execute(
        select(func.count()).select_from(MedicalRecord).where(MedicalRecord.template_id == tpl_id)
    )
    if int(in_use_res.scalar_one()) > 0:
        return err(409, "模板被引用，无法删除")
    tpl = await session.get(RecordTemplate, tpl_id)
    if not tpl:
        return err(404, "Template not found")
    await session.delete(tpl)
    await session.commit()
    return ok({"id": tpl_id}, "模板删除成功")
