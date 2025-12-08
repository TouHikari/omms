from datetime import datetime, date, time
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response import err, ok
from app.db.session import get_session
from app.models.appointment import Schedule, Doctor, Department, Appointment
from app.schemas.appointment import (
    ScheduleOut,
    ScheduleListResponse,
)

router = APIRouter()


@router.get(
    "/schedules",
    summary="排班查询",
    description="查询医生排班信息，支持按科室、医生、日期筛选",
    response_model=ScheduleListResponse,
)
async def list_schedules(
    deptId: Optional[int] = Query(default=None),
    doctorId: Optional[int] = Query(default=None),
    workDate: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """查询排班列表"""
    # 计算分页偏移量
    offset = (page - 1) * pageSize
    
    # 构建查询语句
    stmt = select(Schedule, Doctor.doctor_name, Department.dept_name).join(
        Doctor, Schedule.doctor_id == Doctor.doctor_id
    ).join(Department, Doctor.dept_id == Department.dept_id)
    
    if deptId:
        stmt = stmt.where(Doctor.dept_id == deptId)
    if doctorId:
        stmt = stmt.where(Schedule.doctor_id == doctorId)
    if workDate:
        try:
            work_date_obj = datetime.strptime(workDate, "%Y-%m-%d").date()
            stmt = stmt.where(Schedule.work_date == work_date_obj)
        except ValueError:
            return err(400, "workDate 格式错误，应为 YYYY-MM-DD")
    
    # 查询总数
    total_stmt = select(func.count()).select_from(stmt.subquery())
    total_res = await session.execute(total_stmt)
    total = int(total_res.scalar_one())
    
    # 查询分页数据
    stmt = stmt.order_by(Schedule.work_date, Schedule.schedule_id).offset(offset).limit(pageSize)
    res = await session.execute(stmt)
    
    # 构建响应数据
    schedule_list = []
    for schedule, doctor_name, dept_name in res:
        # 查询已预约数量
        booked_stmt = select(func.count()).select_from(Appointment).where(
            (Appointment.schedule_id == schedule.schedule_id) & (Appointment.status != 2)  # 排除已取消的预约
        )
        booked_res = await session.execute(booked_stmt)
        booked_count = int(booked_res.scalar_one())
        
        # 将日期与时间格式化为字符串
        work_date_str = (
            schedule.work_date.strftime("%Y-%m-%d")
            if hasattr(schedule.work_date, "strftime")
            else str(schedule.work_date)
        )
        start_time_str = (
            schedule.start_time.strftime("%H:%M")
            if hasattr(schedule.start_time, "strftime")
            else str(schedule.start_time)
        )
        end_time_str = (
            schedule.end_time.strftime("%H:%M")
            if hasattr(schedule.end_time, "strftime")
            else str(schedule.end_time)
        )
        # 根据start_time和end_time生成workPeriod
        work_period = f"{start_time_str} - {end_time_str}"
        
        # 获取医生信息以获取dept_id
        doctor_stmt = select(Doctor.dept_id).where(Doctor.doctor_id == schedule.doctor_id)
        doctor_res = await session.execute(doctor_stmt)
        dept_id = doctor_res.scalar_one()
        
        schedule_list.append(
            ScheduleOut(
                scheduleId=schedule.schedule_id,
                doctorId=schedule.doctor_id,
                doctorName=doctor_name,
                deptId=dept_id,
                deptName=dept_name,
                workDate=work_date_str,
                workPeriod=work_period,
                startTime=start_time_str,
                endTime=end_time_str,
                totalQuota=schedule.max_appointments,
                bookedCount=booked_count,
                availableQuota=schedule.max_appointments - booked_count,
                status=schedule.status,
            )
        )
    
    return ok({
        "list": schedule_list,
        "total": total,
        "page": page,
        "pageSize": pageSize
    })
