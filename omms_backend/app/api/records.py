import json
import random
from datetime import datetime, date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response import err, ok
from app.db.session import get_session
from app.models.record import MedicalRecord, RecordTemplate
from app.models.appointment import Department, Doctor
from app.models.patient import Patient
from app.schemas.record import (
    RecordCreate,
    RecordUpdate,
    TemplateCreate,
    TemplateUpdate,
    MedicalRecordOut,
    RecordsListResponse,
    RecordResponse,
    RecordStatusResponse,
    RecordStatusUpdate,
    DeleteRecordResponse,
    RecordTemplateOut,
    RecordTemplateListResponse,
    RecordTemplateResponse,
    TemplateDeleteResponse,
)
from app.schemas.patient import PatientsListResponse, PatientResponse
from app.schemas.record import RecordsStatsResponse, DictionariesResponse, DictionaryArrayResponse


router = APIRouter(tags=["records"])


def gen_record_id(date_str: str) -> str:
    return f"MR-{date_str.replace('-', '')}-{str(random.randint(0, 9999)).zfill(4)}"


def now_date_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def compose_time(date_str: str, hhmm: Optional[str]) -> str:
    return f"{date_str} {hhmm or datetime.now().strftime('%H:%M')}"


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


def to_date_str(val: Optional[object]) -> Optional[str]:
    if not val:
        return None
    if isinstance(val, datetime):
        return val.strftime("%Y-%m-%d")
    if isinstance(val, date):
        return val.strftime("%Y-%m-%d")
    s = str(val)
    return s if s.strip() else None


@router.get(
    "/records",
    summary="病历列表查询",
    description="按状态、日期或日期范围、科室、医生、患者关键词筛选病历列表，支持分页与检验/影像过滤。",
    response_model=RecordsListResponse,
)
async def list_records(
    status: Optional[str] = Query(default=None),
    date: Optional[str] = Query(default=None),
    dateStart: Optional[str] = Query(default=None),
    dateEnd: Optional[str] = Query(default=None),
    patientKeyword: Optional[str] = Query(default=None),
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
    if dateStart and dateEnd:
        stmt = stmt.where(MedicalRecord.created_at >= f"{dateStart} 00:00").where(MedicalRecord.created_at <= f"{dateEnd} 23:59")
    elif date:
        stmt = stmt.where(MedicalRecord.created_at.like(f"{date}%"))
    if deptId:
        stmt = stmt.where(MedicalRecord.dept_id == deptId)
    if doctorId:
        stmt = stmt.where(MedicalRecord.doctor_id == doctorId)
    if patientKeyword:
        kw = "".join((patientKeyword or "").split()).lower()
        stmt = stmt.where(func.lower(func.replace(MedicalRecord.patient_name, " ", "")).like(f"%{kw}%"))

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
    ok_rel, msg = await check_doctor_dept(session, payload.deptId, payload.doctorId)
    if not ok_rel:
        return err(400, msg)
    created_at_raw = payload.createdAt or compose_time(now_date_str(), payload.time)
    try:
        ca_dt = datetime.strptime(created_at_raw, "%Y-%m-%d %H:%M")
        if ca_dt > datetime.now():
            return err(400, "createdAt不可晚于当前时间")
    except Exception:
        return err(400, "时间格式非法")
    date_str = created_at_raw.split(" ")[0]
    rid = gen_record_id(date_str)
    created_at = created_at_raw
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
    target_dept_id = rec.dept_id if payload.deptId is None else payload.deptId
    target_doctor_id = rec.doctor_id if payload.doctorId is None else payload.doctorId
    ok_rel, msg = await check_doctor_dept(session, target_dept_id, target_doctor_id)
    if not ok_rel:
        return err(400, msg)
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
async def update_record_status(id: str, payload: RecordStatusUpdate, session: AsyncSession = Depends(get_session)):
    status = (payload.status or "").strip()
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

async def check_doctor_dept(session: AsyncSession, dept_id: int, doctor_id: int):
    dept = await session.get(Department, dept_id)
    if not dept:
        return False, "科室不存在"
    doc = await session.get(Doctor, doctor_id)
    if not doc:
        return False, "医生不存在"
    if doc.dept_id != dept.dept_id:
        return False, "医生不属于该科室"
    return True, ""

# 已移除严格创建/更新端点，统一使用 /records 与 /records/{id}

@router.get(
    "/records/stats",
    summary="病历统计数据",
    description="返回病历的统计数据（支持日期或区间、科室/医生过滤）",
    response_model=RecordsStatsResponse,
)
async def records_stats(
    date: Optional[str] = Query(default=None),
    dateStart: Optional[str] = Query(default=None),
    dateEnd: Optional[str] = Query(default=None),
    deptId: Optional[int] = Query(default=None),
    doctorId: Optional[int] = Query(default=None),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(MedicalRecord)
    if deptId:
        stmt = stmt.where(MedicalRecord.dept_id == deptId)
    if doctorId:
        stmt = stmt.where(MedicalRecord.doctor_id == doctorId)
    if dateStart and dateEnd:
        stmt = stmt.where(MedicalRecord.created_at >= f"{dateStart} 00:00").where(MedicalRecord.created_at <= f"{dateEnd} 23:59")
    elif date:
        stmt = stmt.where(MedicalRecord.created_at.like(f"{date}%"))
    total = int((await session.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one())
    draft = int((await session.execute(select(func.count()).select_from(stmt.where(MedicalRecord.status == "draft").subquery()))).scalar_one())
    finalized = int((await session.execute(select(func.count()).select_from(stmt.where(MedicalRecord.status == "finalized").subquery()))).scalar_one())
    cancelled = int((await session.execute(select(func.count()).select_from(stmt.where(MedicalRecord.status == "cancelled").subquery()))).scalar_one())
    withLab = int((await session.execute(select(func.count()).select_from(stmt.where(func.length(MedicalRecord.labs_json) > 2).subquery()))).scalar_one())
    withImaging = int((await session.execute(select(func.count()).select_from(stmt.where(func.length(MedicalRecord.imaging_json) > 2).subquery()))).scalar_one())
    return ok({"total": total, "draft": draft, "finalized": finalized, "cancelled": cancelled, "withLab": withLab, "withImaging": withImaging})

@router.get(
    "/records/dictionaries",
    summary="病历词典数据",
    description="返回病历录入相关的词典数据集合",
    response_model=DictionariesResponse,
)
async def records_dictionaries(session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(MedicalRecord).where(or_(func.length(MedicalRecord.imaging_json) > 2, func.length(MedicalRecord.labs_json) > 2)))
    imaging_set, labs_set = set(), set()
    for r in res.scalars().all():
        for v in to_list(r.imaging_json):
            if isinstance(v, str) and v.strip():
                imaging_set.add(v.strip())
        for v in to_list(r.labs_json):
            if isinstance(v, str) and v.strip():
                labs_set.add(v.strip())
    tpl_res = await session.execute(select(RecordTemplate))
    for tpl in tpl_res.scalars().all():
        try:
            d = json.loads(tpl.defaults_json or "{}")
        except Exception:
            d = {}
        for v in (d.get("imaging") or []):
            if isinstance(v, str) and v.strip():
                imaging_set.add(v.strip())
        for v in (d.get("labs") or []):
            if isinstance(v, str) and v.strip():
                labs_set.add(v.strip())
    return ok({"imaging": sorted(list(imaging_set)), "labs": sorted(list(labs_set))})

@router.get(
    "/records/dictionaries/imaging",
    summary="影像词典",
    description="返回影像项目词典",
    response_model=DictionaryArrayResponse,
)
async def records_dictionaries_imaging(session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(MedicalRecord).where(func.length(MedicalRecord.imaging_json) > 2))
    imaging_set = set()
    for r in res.scalars().all():
        for v in to_list(r.imaging_json):
            if isinstance(v, str) and v.strip():
                imaging_set.add(v.strip())
    tpl_res = await session.execute(select(RecordTemplate))
    for tpl in tpl_res.scalars().all():
        try:
            d = json.loads(tpl.defaults_json or "{}")
        except Exception:
            d = {}
        for v in (d.get("imaging") or []):
            if isinstance(v, str) and v.strip():
                imaging_set.add(v.strip())
    return ok(sorted(list(imaging_set)))

@router.get(
    "/records/dictionaries/labs",
    summary="检验词典",
    description="返回检验项目词典",
    response_model=DictionaryArrayResponse,
)
async def records_dictionaries_labs(session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(MedicalRecord).where(func.length(MedicalRecord.labs_json) > 2))
    labs_set = set()
    for r in res.scalars().all():
        for v in to_list(r.labs_json):
            if isinstance(v, str) and v.strip():
                labs_set.add(v.strip())
    tpl_res = await session.execute(select(RecordTemplate))
    for tpl in tpl_res.scalars().all():
        try:
            d = json.loads(tpl.defaults_json or "{}")
        except Exception:
            d = {}
        for v in (d.get("labs") or []):
            if isinstance(v, str) and v.strip():
                labs_set.add(v.strip())
    return ok(sorted(list(labs_set)))

@router.get(
    "/patients",
    summary="患者资料查询",
    description="按姓名关键词查询患者基本资料，忽略大小写与空格，支持分页",
    response_model=PatientsListResponse,
)
async def get_patients(
    name: Optional[str] = Query(default=None),
    page: int = Query(default=1),
    pageSize: int = Query(default=20),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Patient)
    if name:
        kw = "".join((name or "").split()).lower()
        stmt = stmt.where(func.lower(func.replace(Patient.name, " ", "")).like(f"%{kw}%"))
    total_res = await session.execute(select(func.count()).select_from(stmt.subquery()))
    total = int(total_res.scalar_one())
    res = await session.execute(stmt.order_by(Patient.patient_id.desc()))
    all_items = []
    for p in res.scalars().all():
        all_items.append({
            "patientId": p.patient_id,
            "userId": p.user_id,
            "name": p.name,
            "gender": p.gender,
            "birthday": to_date_str(p.birthday),
            "idCard": p.id_card,
            "address": p.address,
            "emergencyContact": p.emergency_contact,
            "emergencyPhone": p.emergency_phone,
        })
    start = max(0, (page - 1) * pageSize)
    end = start + pageSize
    return ok({"list": all_items[start:end], "total": total, "page": page, "pageSize": pageSize})

@router.get(
    "/patients/{pid}",
    summary="患者资料详情",
    description="按患者唯一标识获取患者详细资料",
    response_model=PatientResponse,
)
async def get_patient_by_id(pid: int, session: AsyncSession = Depends(get_session)):
    p = await session.get(Patient, pid)
    if not p:
        return err(404, "Patient not found")
    return ok({
        "patientId": p.patient_id,
        "userId": p.user_id,
        "name": p.name,
        "gender": p.gender,
        "birthday": to_date_str(p.birthday),
        "idCard": p.id_card,
        "address": p.address,
        "emergencyContact": p.emergency_contact,
        "emergencyPhone": p.emergency_phone,
    })

@router.get(
    "/records-ext",
    summary="病历列表查询（扩展筛选）",
    description="支持患者关键词与日期范围筛选，返回与 /records 相同结构",
    response_model=RecordsListResponse,
)
async def list_records_extended(
    status: Optional[str] = Query(default=None),
    patientKeyword: Optional[str] = Query(default=None),
    deptId: Optional[int] = Query(default=None),
    doctorId: Optional[int] = Query(default=None),
    hasLab: Optional[bool] = Query(default=None),
    hasImaging: Optional[bool] = Query(default=None),
    date: Optional[str] = Query(default=None),
    dateStart: Optional[str] = Query(default=None),
    dateEnd: Optional[str] = Query(default=None),
    page: int = Query(default=1),
    pageSize: int = Query(default=20),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(MedicalRecord)
    if status:
        stmt = stmt.where(MedicalRecord.status == status)
    if deptId:
        stmt = stmt.where(MedicalRecord.dept_id == deptId)
    if doctorId:
        stmt = stmt.where(MedicalRecord.doctor_id == doctorId)
    if dateStart and dateEnd:
        stmt = stmt.where(MedicalRecord.created_at >= f"{dateStart} 00:00").where(MedicalRecord.created_at <= f"{dateEnd} 23:59")
    elif date:
        stmt = stmt.where(MedicalRecord.created_at.like(f"{date}%"))
    if patientKeyword:
        kw = "".join((patientKeyword or "").split()).lower()
        stmt = stmt.where(func.lower(func.replace(MedicalRecord.patient_name, " ", "")).like(f"%{kw}%"))
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
