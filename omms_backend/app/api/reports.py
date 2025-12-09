from datetime import datetime, timedelta
from typing import Optional, List, Dict

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, and_, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response import ok, err
from app.db.session import get_session
from app.models.appointment import Appointment, Doctor, Department
from app.models.patient import Patient
from app.models.prescription import Prescription, PrescriptionItem
from app.models.medicine import Medicine
from app.schemas.reports import (
    DailyVisitsResponse,
    DailyDrugsResponse,
    MonthlyVisitsResponse,
    MonthlyDrugsResponse,
    CustomReportResponse,
)


router = APIRouter(tags=["reports"])


def status_str(status_int: Optional[int]) -> str:
    if status_int == 1:
        return "completed"
    if status_int == 2:
        return "cancelled"
    return "pending"


@router.get(
    "/reports/daily/visits",
    summary="获取就诊日报",
    description="按日期查询就诊日报数据",
    response_model=DailyVisitsResponse,
)
async def get_daily_visits(
    date: str = Query(..., description="日期（YYYY-MM-DD）"),
    session: AsyncSession = Depends(get_session),
):
    try:
        day_start = datetime.strptime(date, "%Y-%m-%d")
        day_end = day_start + timedelta(days=1)
    except Exception:
        return err(400, "日期格式错误")

    stmt = (
        select(
            Appointment,
            Patient.name.label("patient_name"),
            Doctor.doctor_name,
            Department.dept_name,
        )
        .join(Patient, Appointment.patient_id == Patient.patient_id)
        .join(Doctor, Appointment.doctor_id == Doctor.doctor_id)
        .join(Department, Doctor.dept_id == Department.dept_id)
        .where(and_(Appointment.appt_time >= day_start, Appointment.appt_time < day_end))
        .order_by(Appointment.appt_time.asc())
    )
    res = await session.execute(stmt)
    rows = res.all()
    data_list = []
    for appt, patient_name, doctor_name, dept_name in rows:
        date_str = appt.appt_time.strftime("%Y-%m-%d") if appt.appt_time else ""
        num = str(appt.appt_id or 0)
        padded = num[-4:] if len(num) >= 4 else num.zfill(4)
        rid = f"R-{date_str.replace('-', '')}-{padded}"
        data_list.append(
            {
                "id": rid,
                "patient": patient_name,
                "department": dept_name,
                "doctor": doctor_name,
                "time": appt.appt_time.strftime("%Y-%m-%d %H:%M:%S") if appt.appt_time else None,
                "status": status_str(appt.status),
            }
        )

    return ok({"list": data_list, "total": len(data_list)})


@router.get(
    "/reports/daily/drugs",
    summary="获取药品使用日报",
    description="按日期查询药品使用日报数据",
    response_model=DailyDrugsResponse,
)
async def get_daily_drugs(
    date: str = Query(..., description="日期（YYYY-MM-DD）"),
    session: AsyncSession = Depends(get_session),
):
    try:
        day_start = datetime.strptime(date, "%Y-%m-%d")
        day_end = day_start + timedelta(days=1)
    except Exception:
        return err(400, "日期格式错误")

    p_stmt = (
        select(Prescription)
        .where(and_(Prescription.created_at >= day_start, Prescription.created_at < day_end))
        .order_by(Prescription.created_at.asc())
    )
    prescriptions: List[Prescription] = (await session.execute(p_stmt)).scalars().all()
    pids = [p.id for p in prescriptions]
    items: List[PrescriptionItem] = []
    if pids:
        i_stmt = select(PrescriptionItem).where(PrescriptionItem.prescription_id.in_(pids))
        items = (await session.execute(i_stmt)).scalars().all()
    # prefetch medicines
    mids = {i.medicine_id for i in items}
    med_map: Dict[int, Medicine] = {}
    if mids:
        meds = (await session.execute(select(Medicine).where(Medicine.medicine_id.in_(list(mids))))).scalars().all()
        med_map = {m.medicine_id: m for m in meds}
    # index prescriptions
    p_map = {p.id: p for p in prescriptions}

    data_list = []
    for i in items:
        p = p_map.get(i.prescription_id)
        if not p:
            # skip orphan
            continue
        med = med_map.get(i.medicine_id)
        date_str = p.created_at.strftime("%Y-%m-%d") if p.created_at else ""
        row = {
            "id": f"{p.id}-{i.id}",
            "medicine": (med.medicine_name if med else (i.name or "")),
            "specification": (med.specification if med else None),
            "quantity": int(i.qty or 0),
            "unit": i.unit,
            "patient": p.patient,
            "department": p.department,
            "doctor": p.doctor,
            "date": date_str,
        }
        # front-end expects no unit column now, but keep in payload for future
        data_list.append(row)

    return ok({"list": data_list, "total": len(data_list)})


@router.get(
    "/reports/monthly/visits",
    summary="获取就诊月报",
    description="按月份统计每日就诊数量",
    response_model=MonthlyVisitsResponse,
)
async def get_monthly_visits(
    month: str = Query(..., description="月份（YYYY-MM）"),
    session: AsyncSession = Depends(get_session),
):
    try:
        month_start = datetime.strptime(month + "-01", "%Y-%m-%d")
        # add ~32 days then clamp to first of next month
        approx_next = month_start + timedelta(days=32)
        month_end = datetime.strptime(approx_next.strftime("%Y-%m") + "-01", "%Y-%m-%d")
    except Exception:
        return err(400, "月份格式错误")

    # group by date
    stmt = (
        select(
            func.date_format(Appointment.appt_time, "%Y-%m-%d").label("d"),
            func.count().label("c"),
        )
        .where(and_(Appointment.appt_time >= month_start, Appointment.appt_time < month_end))
        .group_by(text("d"))
        .order_by(text("d"))
    )
    res = await session.execute(stmt)
    rows = res.all()
    data_list = [{"date": d, "count": int(c or 0)} for d, c in rows]
    return ok({"list": data_list, "totalDays": len(data_list)})


@router.get(
    "/reports/monthly/drugs",
    summary="获取药品使用月报",
    description="按月份统计每日药品项数",
    response_model=MonthlyDrugsResponse,
)
async def get_monthly_drugs(
    month: str = Query(..., description="月份（YYYY-MM）"),
    session: AsyncSession = Depends(get_session),
):
    try:
        month_start = datetime.strptime(month + "-01", "%Y-%m-%d")
        approx_next = month_start + timedelta(days=32)
        month_end = datetime.strptime(approx_next.strftime("%Y-%m") + "-01", "%Y-%m-%d")
    except Exception:
        return err(400, "月份格式错误")

    # group by prescription created_at day and sum item count
    p_stmt = select(Prescription).where(and_(Prescription.created_at >= month_start, Prescription.created_at < month_end))
    prescriptions: List[Prescription] = (await session.execute(p_stmt)).scalars().all()
    pids = [p.id for p in prescriptions]
    # count items per prescription
    counts_by_pid: Dict[str, int] = {}
    if pids:
        i_stmt = (
            select(PrescriptionItem.prescription_id, func.count().label("cnt"))
            .where(PrescriptionItem.prescription_id.in_(pids))
            .group_by(PrescriptionItem.prescription_id)
        )
        for pid, cnt in (await session.execute(i_stmt)).all():
            counts_by_pid[str(pid)] = int(cnt or 0)

    items_by_day: Dict[str, int] = {}
    for p in prescriptions:
        d = p.created_at.strftime("%Y-%m-%d") if p.created_at else None
        if not d:
            continue
        items_by_day[d] = int(items_by_day.get(d, 0)) + int(counts_by_pid.get(str(p.id), 0))

    data_list = [{"date": d, "items": items_by_day[d]} for d in sorted(items_by_day.keys())]
    return ok({"list": data_list, "totalDays": len(data_list)})


@router.get(
    "/reports/custom",
    summary="自定义报表数据",
    description="按筛选条件返回包含就诊与处方聚合的行数据",
    response_model=CustomReportResponse,
)
async def get_custom_report(
    deptName: Optional[str] = Query(default=None, description="科室名称"),
    doctorName: Optional[str] = Query(default=None, description="医生姓名"),
    dateStart: Optional[str] = Query(default=None, description="开始日期（YYYY-MM-DD）"),
    dateEnd: Optional[str] = Query(default=None, description="结束日期（YYYY-MM-DD）"),
    session: AsyncSession = Depends(get_session),
):
    # build date range
    start_dt: Optional[datetime] = None
    end_dt: Optional[datetime] = None
    try:
        if dateStart:
            start_dt = datetime.strptime(dateStart, "%Y-%m-%d")
        if dateEnd:
            end_dt = datetime.strptime(dateEnd, "%Y-%m-%d") + timedelta(days=1)
    except Exception:
        return err(400, "日期格式错误")

    stmt = (
        select(
            Appointment,
            Patient.name.label("patient_name"),
            Doctor.doctor_name,
            Department.dept_name,
        )
        .join(Patient, Appointment.patient_id == Patient.patient_id)
        .join(Doctor, Appointment.doctor_id == Doctor.doctor_id)
        .join(Department, Doctor.dept_id == Department.dept_id)
    )
    if deptName:
        stmt = stmt.where(Department.dept_name == deptName)
    if doctorName:
        stmt = stmt.where(Doctor.doctor_name == doctorName)
    if start_dt:
        stmt = stmt.where(Appointment.appt_time >= start_dt)
    if end_dt:
        stmt = stmt.where(Appointment.appt_time < end_dt)
    stmt = stmt.order_by(Appointment.appt_time.asc())

    res = await session.execute(stmt)
    rows = res.all()

    # 预抓处方，并按 day|doctor|department 聚合条目数
    # 这样即使同一医生当日为不同患者开具处方，也能正确计数
    days: Dict[str, None] = {}
    for appt, _, _, _ in rows:
        if appt.appt_time:
            days[appt.appt_time.strftime("%Y-%m-%d")] = None
    if days:
        p_stmt = select(Prescription).where(
            and_(
                (start_dt or datetime.min) <= Prescription.created_at,
                Prescription.created_at < (end_dt or datetime.max),
            )
        )
        prescriptions: List[Prescription] = (await session.execute(p_stmt)).scalars().all()
        pids = [p.id for p in prescriptions]
        item_count_by_pid: Dict[str, int] = {}
        if pids:
            i_stmt = (
                select(PrescriptionItem.prescription_id, func.count().label("cnt"))
                .where(PrescriptionItem.prescription_id.in_(pids))
                .group_by(PrescriptionItem.prescription_id)
            )
            for pid, cnt in (await session.execute(i_stmt)).all():
                item_count_by_pid[str(pid)] = int(cnt or 0)
        # sum by day|doctor|department
        items_by_dday: Dict[str, int] = {}
        for p in prescriptions:
            d = p.created_at.strftime("%Y-%m-%d") if p.created_at else None
            if not d:
                continue
            key = f"{d}|{p.doctor}|{p.department}"
            items_by_dday[key] = int(items_by_dday.get(key, 0)) + int(item_count_by_pid.get(str(p.id), 0))
    else:
        items_by_dday = {}

    data_list = []
    for appt, patient_name, doctor_name, dept_name in rows:
        tstr = appt.appt_time.strftime("%Y-%m-%d %H:%M:%S") if appt.appt_time else None
        day = appt.appt_time.strftime("%Y-%m-%d") if appt.appt_time else ""
        num = str(appt.appt_id or 0)
        padded = num[-4:] if len(num) >= 4 else num.zfill(4)
        rid = f"R-{day.replace('-', '')}-{padded}"
        key_dday = f"{day}|{doctor_name}|{dept_name}"
        total_items = int(items_by_dday.get(key_dday, 0))
        data_list.append(
            {
                "id": rid,
                "patient": patient_name,
                "department": dept_name,
                "doctor": doctor_name,
                "time": tstr,
                "status": status_str(appt.status),
                "drugItems": total_items,
            }
        )

    return ok({"list": data_list, "total": len(data_list)})
