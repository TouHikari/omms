from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response import err, ok
from app.db.session import get_session
from app.models.appointment import Appointment, Doctor, Department
from app.models.patient import Patient
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentOut,
    AppointmentListResponse,
    AppointmentResponse,
    DeleteResponse,
)

router = APIRouter()


@router.get(
    "/appointments",
    summary="预约列表查询",
    description="查询预约列表，支持按患者、医生、状态筛选和分页查询",
    response_model=AppointmentListResponse,
)
async def list_appointments(
    patientId: Optional[int] = Query(default=None),
    doctorId: Optional[int] = Query(default=None),
    status: Optional[int] = Query(default=None),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """查询预约列表"""
    # 计算分页偏移量
    offset = (page - 1) * pageSize
    
    # 构建查询语句
    stmt = select(
        Appointment,
        Patient.name.label('patient_name'),
        Doctor.doctor_name,
        Department.dept_name,
        Doctor.dept_id.label('dept_id'),
    ).join(Patient, Appointment.patient_id == Patient.patient_id).join(
        Doctor, Appointment.doctor_id == Doctor.doctor_id
    ).join(Department, Doctor.dept_id == Department.dept_id)
    
    if patientId:
        stmt = stmt.where(Appointment.patient_id == patientId)
    if doctorId:
        stmt = stmt.where(Appointment.doctor_id == doctorId)
    if status is not None:
        stmt = stmt.where(Appointment.status == status)
    
    # 查询总数
    total_stmt = select(func.count()).select_from(stmt.subquery())
    total_res = await session.execute(total_stmt)
    total = int(total_res.scalar_one())
    
    # 查询分页数据
    stmt = stmt.order_by(Appointment.appt_time.desc()).offset(offset).limit(pageSize)
    res = await session.execute(stmt)
    
    # 构建响应数据
    appointment_list = []
    for appointment, patient_name, doctor_name, dept_name, dept_id in res:
        appointment_list.append(
            AppointmentOut(
                apptId=appointment.appt_id,
                patientId=appointment.patient_id,
                patientName=patient_name,
                doctorId=appointment.doctor_id,
                doctorName=doctor_name,
                deptId=dept_id,
                deptName=dept_name,
                scheduleId=appointment.schedule_id,
                apptTime=appointment.appt_time.strftime("%Y-%m-%d %H:%M:%S") if appointment.appt_time else None,
                status=appointment.status,
                symptomDesc=appointment.symptom_desc,
                createdAt=appointment.created_at,
                updatedAt=appointment.updated_at,
            )
        )
    
    return ok({
        "list": appointment_list,
        "total": total,
        "page": page,
        "pageSize": pageSize
    })


@router.post(
    "/appointments",
    summary="创建预约",
    description="创建新的预约信息",
    response_model=AppointmentResponse,
)
async def create_appointment(
    payload: AppointmentCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """创建预约"""
    patient = await session.get(Patient, payload.patientId)
    if not patient:
        res = await session.execute(select(Patient).where(Patient.user_id == payload.patientId))
        patient = res.scalars().first()
    if not patient:
        res = await session.execute(select(Patient).where(Patient.user_id == current_user.user_id))
        patient = res.scalars().first()
    if not patient:
        return err(400, "患者不存在")
    
    # 检查医生是否存在
    doctor = await session.get(Doctor, payload.doctorId)
    if not doctor:
        return err(400, "医生不存在")
    
    # 检查排班是否存在
    from app.models.appointment import Schedule
    schedule = await session.get(Schedule, payload.scheduleId)
    if not schedule:
        return err(400, "排班不存在")
    
    # 检查排班是否属于该医生
    if schedule.doctor_id != payload.doctorId:
        return err(400, "排班不属于该医生")
    
    # 检查预约时间是否在排班时间内
    appt_time = datetime.strptime(payload.apptTime, "%Y-%m-%d %H:%M:%S")
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
    schedule_start = datetime.strptime(f"{work_date_str} {start_time_str}", "%Y-%m-%d %H:%M")
    schedule_end = datetime.strptime(f"{work_date_str} {end_time_str}", "%Y-%m-%d %H:%M")
    
    if not (schedule_start <= appt_time <= schedule_end):
        return err(400, "预约时间不在排班时间内")
    
    # 检查预约数量是否超过限额
    booked_stmt = select(func.count()).select_from(Appointment).where(
        (Appointment.schedule_id == payload.scheduleId) & (Appointment.status != 2)  # 排除已取消的预约
    )
    booked_res = await session.execute(booked_stmt)
    booked_count = int(booked_res.scalar_one())
    
    if booked_count >= schedule.max_appointments:
        return err(400, "该时段预约已满")
    
    # 检查患者是否在同一时间段已有预约
    actual_patient_id = patient.patient_id
    existing_stmt = select(Appointment).where(
        (Appointment.patient_id == actual_patient_id) & 
        (Appointment.appt_time == appt_time) & 
        (Appointment.status != 2)  # 排除已取消的预约
    )
    existing_res = await session.execute(existing_stmt)
    if existing_res.scalars().first():
        return err(400, "该时间段已有预约")
    
    # 创建预约
    now = datetime.now()
    # 将字符串格式的appt_time转换为datetime对象
    appt_time = datetime.strptime(payload.apptTime, "%Y-%m-%d %H:%M:%S")
    appointment = Appointment(
        patient_id=actual_patient_id,
        doctor_id=payload.doctorId,
        schedule_id=payload.scheduleId,
        appt_time=appt_time,
        status=0,  # 待确认状态
        symptom_desc=payload.symptomDesc,
        created_at=now,
        updated_at=now,
    )
    
    session.add(appointment)
    await session.commit()
    await session.refresh(appointment)
    
    # 获取患者姓名、医生姓名和科室名称
    patient_name = patient.name
    doctor_name = doctor.doctor_name
    dept_res = await session.execute(select(Department.dept_name).where(Department.dept_id == doctor.dept_id))
    dept_name = dept_res.scalar_one_or_none() or ''
    
    return ok(
        AppointmentOut(
            apptId=appointment.appt_id,
            patientId=appointment.patient_id,
            patientName=patient_name,
            doctorId=appointment.doctor_id,
            doctorName=doctor_name,
            deptId=doctor.dept_id,
            deptName=dept_name,
            scheduleId=appointment.schedule_id,
            apptTime=appointment.appt_time.strftime("%Y-%m-%d %H:%M:%S"),
            status=appointment.status,
            symptomDesc=appointment.symptom_desc,
            createdAt=appointment.created_at,
            updatedAt=appointment.updated_at,
        ),
        "预约创建成功"
    )


@router.get(
    "/appointments/{appt_id}",
    summary="预约详情",
    description="根据预约ID获取预约详情",
    response_model=AppointmentResponse,
)
async def get_appointment(
    appt_id: int,
    session: AsyncSession = Depends(get_session),
):
    """获取预约详情"""
    stmt = select(
        Appointment,
        Patient.name.label('patient_name'),
        Doctor.doctor_name,
        Department.dept_name,
        Doctor.dept_id.label('dept_id'),
    ).join(Patient, Appointment.patient_id == Patient.patient_id).join(
        Doctor, Appointment.doctor_id == Doctor.doctor_id
    ).join(Department, Doctor.dept_id == Department.dept_id).where(Appointment.appt_id == appt_id)
    
    res = await session.execute(stmt)
    result = res.first()
    
    if not result:
        return err(404, "预约不存在")
    
    appointment, patient_name, doctor_name, dept_name, dept_id = result
    
    return ok(
        AppointmentOut(
            apptId=appointment.appt_id,
            patientId=appointment.patient_id,
            patientName=patient_name,
            doctorId=appointment.doctor_id,
            doctorName=doctor_name,
            deptId=dept_id,
            deptName=dept_name,
            scheduleId=appointment.schedule_id,
            apptTime=appointment.appt_time.strftime("%Y-%m-%d %H:%M:%S"),
            status=appointment.status,
            symptomDesc=appointment.symptom_desc,
            createdAt=appointment.created_at,
            updatedAt=appointment.updated_at,
        )
    )


@router.put(
    "/appointments/{appt_id}",
    summary="更新预约",
    description="更新预约信息",
    response_model=AppointmentResponse,
)
async def update_appointment(
    appt_id: int,
    payload: AppointmentUpdate,
    session: AsyncSession = Depends(get_session),
):
    """更新预约"""
    appointment = await session.get(Appointment, appt_id)
    if not appointment:
        return err(404, "预约不存在")
    
    # 更新字段
    if payload.status is not None:
        appointment.status = payload.status
    if payload.symptomDesc is not None:
        appointment.symptom_desc = payload.symptomDesc
    
    appointment.updated_at = datetime.now()
    await session.commit()
    
    # 获取患者姓名、医生姓名和科室名称
    stmt = select(
        Patient.name.label('patient_name'),
        Doctor.doctor_name,
        Department.dept_name,
        Doctor.dept_id.label('dept_id'),
    ).select_from(Appointment).join(Patient, Appointment.patient_id == Patient.patient_id).join(
        Doctor, Appointment.doctor_id == Doctor.doctor_id
    ).join(Department, Doctor.dept_id == Department.dept_id).where(Appointment.appt_id == appt_id)
    
    res = await session.execute(stmt)
    result = res.first()
    
    if not result:
        return err(404, "预约详情获取失败")
    
    patient_name, doctor_name, dept_name, dept_id = result
    
    return ok(
        AppointmentOut(
            apptId=appointment.appt_id,
            patientId=appointment.patient_id,
            patientName=patient_name,
            doctorId=appointment.doctor_id,
            doctorName=doctor_name,
            deptId=dept_id,
            deptName=dept_name,
            scheduleId=appointment.schedule_id,
            apptTime=appointment.appt_time.strftime("%Y-%m-%d %H:%M:%S") if appointment.appt_time else None,
            status=appointment.status,
            symptomDesc=appointment.symptom_desc,
            createdAt=appointment.created_at,
            updatedAt=appointment.updated_at,
        ),
        "预约更新成功"
    )


@router.patch(
    "/appointments/{appt_id}/status",
    summary="更新预约状态",
    description="更新预约状态信息",
    response_model=AppointmentResponse,
)
async def update_appointment_status(
    appt_id: int,
    payload: AppointmentUpdate,
    session: AsyncSession = Depends(get_session),
):
    """更新预约状态"""
    appointment = await session.get(Appointment, appt_id)
    if not appointment:
        return err(404, "预约不存在")
    
    # 只允许更新状态字段
    if payload.status is not None:
        appointment.status = payload.status
        appointment.updated_at = datetime.now()
        await session.commit()
        await session.refresh(appointment)
    else:
        return err(400, "必须提供状态字段")
    
    # 获取患者姓名、医生姓名和科室名称
    stmt = select(
        Patient.name.label('patient_name'),
        Doctor.doctor_name,
        Department.dept_name,
        Doctor.dept_id.label('dept_id'),
    ).select_from(Appointment).join(Patient, Appointment.patient_id == Patient.patient_id).join(
        Doctor, Appointment.doctor_id == Doctor.doctor_id
    ).join(Department, Doctor.dept_id == Department.dept_id).where(Appointment.appt_id == appt_id)
    
    res = await session.execute(stmt)
    result = res.first()
    
    if not result:
        return err(404, "预约详情获取失败")
    
    patient_name, doctor_name, dept_name, dept_id = result
    
    return ok(
        AppointmentOut(
            apptId=appointment.appt_id,
            patientId=appointment.patient_id,
            patientName=patient_name,
            doctorId=appointment.doctor_id,
            doctorName=doctor_name,
            deptId=dept_id,
            deptName=dept_name,
            scheduleId=appointment.schedule_id,
            apptTime=appointment.appt_time.strftime("%Y-%m-%d %H:%M:%S") if appointment.appt_time else None,
            status=appointment.status,
            symptomDesc=appointment.symptom_desc,
            createdAt=appointment.created_at,
            updatedAt=appointment.updated_at,
        ),
        "预约状态更新成功"
    )

@router.delete(
    "/appointments/{appt_id}",
    summary="取消预约",
    description="取消预约信息",
    response_model=DeleteResponse,
)
async def cancel_appointment(
    appt_id: int,
    session: AsyncSession = Depends(get_session),
):
    """取消预约"""
    appointment = await session.get(Appointment, appt_id)
    if not appointment:
        return err(404, "预约不存在")
    
    # 将状态改为取消
    appointment.status = 2  # 取消预约
    appointment.updated_at = datetime.now()
    await session.commit()
    
    return ok({"apptId": appt_id}, "预约已取消")
