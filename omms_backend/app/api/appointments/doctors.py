from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response import err, ok
from app.db.session import get_session
from app.models.appointment import Doctor, Department, Schedule
from app.models.user import User
from app.models.appointment import Appointment
from app.schemas.appointment import (
    DoctorCreate,
    DoctorUpdate,
    DoctorOut,
    DoctorListResponse,
    DoctorResponse,
    DeleteResponse,
)

router = APIRouter()


@router.get(
    "/doctors",
    summary="医生列表查询",
    description="查询医生列表，支持按科室筛选和分页查询",
    response_model=DoctorListResponse,
)
async def list_doctors(
    deptId: Optional[int] = Query(default=None),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """查询医生列表"""
    # 计算分页偏移量
    offset = (page - 1) * pageSize
    
    # 构建查询语句
    stmt = select(Doctor, Department.dept_name).join(Department, Doctor.dept_id == Department.dept_id)
    
    if deptId:
        stmt = stmt.where(Doctor.dept_id == deptId)
    
    # 查询总数
    total_stmt = select(func.count()).select_from(stmt.subquery())
    total_res = await session.execute(total_stmt)
    total = int(total_res.scalar_one())
    
    # 查询分页数据
    stmt = stmt.order_by(Doctor.doctor_id).offset(offset).limit(pageSize)
    res = await session.execute(stmt)
    
    # 构建响应数据
    doctor_list = []
    for doctor, dept_name in res:
        doctor_list.append(
            DoctorOut(
                doctorId=doctor.doctor_id,
                doctorName=doctor.doctor_name,
                deptId=doctor.dept_id,
                deptName=dept_name,
                title=doctor.title,
                specialty=doctor.specialty,
                introduction=doctor.introduction,
                createdAt=doctor.created_at,
                updatedAt=doctor.updated_at,
            )
        )
    
    return ok({
        "list": doctor_list,
        "total": total,
        "page": page,
        "pageSize": pageSize
    })


@router.post(
    "/doctors",
    summary="创建医生",
    description="创建新的医生信息",
    response_model=DoctorResponse,
)
async def create_doctor(
    payload: DoctorCreate,
    session: AsyncSession = Depends(get_session),
):
    """创建医生"""
    # 检查科室是否存在
    department = await session.get(Department, payload.deptId)
    if not department:
        return err(400, "科室不存在")
    
    # 检查用户是否存在
    user = await session.get(User, payload.userId)
    if not user:
        return err(400, "用户不存在")
    
    # 创建医生
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    doctor = Doctor(
        doctor_name=payload.doctorName,
        dept_id=payload.deptId,
        user_id=payload.userId,
        title=payload.title,
        specialty=payload.specialty,
        introduction=payload.introduction,
        created_at=now,
        updated_at=now,
    )
    
    session.add(doctor)
    await session.commit()
    await session.refresh(doctor)
    
    return ok(
        DoctorOut(
            doctorId=doctor.doctor_id,
            doctorName=doctor.doctor_name,
            deptId=doctor.dept_id,
            deptName=department.dept_name,
            title=doctor.title,
            specialty=doctor.specialty,
            introduction=doctor.introduction,
            createdAt=doctor.created_at,
            updatedAt=doctor.updated_at,
        ),
        "医生创建成功"
    )


@router.get(
    "/doctors/{doctor_id}",
    summary="医生详情",
    description="根据医生ID获取医生详情",
    response_model=DoctorResponse,
)
async def get_doctor(
    doctor_id: int,
    session: AsyncSession = Depends(get_session),
):
    """获取医生详情"""
    try:
        stmt = select(Doctor, Department.dept_name).join(Department, Doctor.dept_id == Department.dept_id).where(Doctor.doctor_id == doctor_id)
        res = await session.execute(stmt)
        result = res.first()
        
        if not result:
            return err(404, "医生不存在")
        
        doctor, dept_name = result
        
        return ok(
            DoctorOut(
                doctorId=doctor.doctor_id,
                doctorName=doctor.doctor_name,
                deptId=doctor.dept_id,
                deptName=dept_name,
                title=doctor.title,
                specialty=doctor.specialty,
                introduction=doctor.introduction,
                createdAt=doctor.created_at,
                updatedAt=doctor.updated_at,
            )
        )
    except Exception as e:
        print(f"Error in get_doctor: {str(e)}")
        import traceback
        traceback.print_exc()
        return err(500, "内部服务器错误")


@router.put(
    "/doctors/{doctor_id}",
    summary="更新医生",
    description="更新医生信息",
    response_model=DoctorResponse,
)
async def update_doctor(
    doctor_id: int,
    payload: DoctorUpdate,
    session: AsyncSession = Depends(get_session),
):
    """更新医生"""
    doctor = await session.get(Doctor, doctor_id)
    if not doctor:
        return err(404, "医生不存在")
    
    # 检查科室是否存在
    if payload.deptId:
        department = await session.get(Department, payload.deptId)
        if not department:
            return err(400, "科室不存在")
    
    # 更新字段
    if payload.doctorName is not None:
        doctor.doctor_name = payload.doctorName
    if payload.deptId is not None:
        doctor.dept_id = payload.deptId
    if payload.title is not None:
        doctor.title = payload.title
    if payload.specialty is not None:
        doctor.specialty = payload.specialty
    if payload.introduction is not None:
        doctor.introduction = payload.introduction
    
    doctor.updated_at = datetime.now()
    await session.commit()
    
    # 获取更新后的科室名称
    department = await session.get(Department, doctor.dept_id)
    
    return ok(
        DoctorOut(
            doctorId=doctor.doctor_id,
            doctorName=doctor.doctor_name,
            deptId=doctor.dept_id,
            deptName=department.dept_name if department else None,
            title=doctor.title,
            specialty=doctor.specialty,
            introduction=doctor.introduction,
            createdAt=doctor.created_at,
            updatedAt=doctor.updated_at,
        ),
        "医生更新成功"
    )


@router.delete(
    "/doctors/{doctor_id}",
    summary="删除医生",
    description="删除医生信息",
    response_model=DeleteResponse,
)
async def delete_doctor(
    doctor_id: int,
    session: AsyncSession = Depends(get_session),
):
    """删除医生"""
    doctor = await session.get(Doctor, doctor_id)
    if not doctor:
        return err(404, "医生不存在")
    
    # 检查是否有排班关联
    schedule_stmt = select(Schedule).where(Schedule.doctor_id == doctor_id)
    schedule_res = await session.execute(schedule_stmt)
    if schedule_res.scalars().first():
        return err(400, "该医生有排班记录，无法删除")
    
    # 检查是否有预约关联
    appointment_stmt = select(Appointment).where(Appointment.doctor_id == doctor_id)
    appointment_res = await session.execute(appointment_stmt)
    if appointment_res.scalars().first():
        return err(400, "该医生有预约记录，无法删除")
    
    await session.delete(doctor)
    await session.commit()
    
    return ok({"doctorId": doctor_id}, "医生删除成功")
