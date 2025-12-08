from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response import err, ok
from app.db.session import get_session
from app.models.appointment import Department
from app.schemas.appointment import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentOut,
    DepartmentListResponse,
    DepartmentResponse,
    DeleteResponse,
)

router = APIRouter()


@router.get(
    "/departments",
    summary="科室列表查询",
    description="查询科室列表，支持分页查询",
    response_model=DepartmentListResponse,
)
async def list_departments(
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """查询科室列表"""
    # 计算分页偏移量
    offset = (page - 1) * pageSize
    
    # 查询总数
    total_stmt = select(func.count()).select_from(Department)
    total_res = await session.execute(total_stmt)
    total = int(total_res.scalar_one())
    
    # 查询分页数据
    stmt = select(Department).order_by(Department.sort_order, Department.dept_id).offset(offset).limit(pageSize)
    res = await session.execute(stmt)
    departments = res.scalars().all()
    
    # 构建响应数据
    department_list = []
    for dept in departments:
        department_list.append(
            DepartmentOut(
                deptId=dept.dept_id,
                deptName=dept.dept_name,
                deptDesc=dept.description,
                parentId=dept.parent_id,
                sortOrder=dept.sort_order,
                createdAt=dept.created_at,
                updatedAt=dept.updated_at,
            )
        )
    
    return ok({
        "list": department_list,
        "total": total,
        "page": page,
        "pageSize": pageSize
    })


@router.post(
    "/departments",
    summary="创建科室",
    description="创建新的科室信息",
    response_model=DepartmentResponse,
)
async def create_department(
    payload: DepartmentCreate,
    session: AsyncSession = Depends(get_session),
):
    """创建科室"""
    # 检查科室名称是否已存在
    exists_stmt = select(Department).where(Department.dept_name == payload.deptName)
    exists_res = await session.execute(exists_stmt)
    if exists_res.scalars().first():
        return err(400, "科室名称已存在")
    
    # 创建科室
    now = datetime.now()
    department = Department(
        dept_name=payload.deptName,
        description=payload.deptDesc,
        parent_id=payload.parentId,
        sort_order=payload.sortOrder,
        created_at=now,
        updated_at=now,
    )
    
    session.add(department)
    await session.commit()
    await session.refresh(department)
    
    return ok(
        DepartmentOut(
            deptId=department.dept_id,
            deptName=department.dept_name,
            deptDesc=department.description,
            parentId=department.parent_id,
            sortOrder=department.sort_order,
            createdAt=department.created_at,
            updatedAt=department.updated_at,
        ),
        "科室创建成功"
    )


@router.get(
    "/departments/{dept_id}",
    summary="科室详情",
    description="根据科室ID获取科室详情",
    response_model=DepartmentResponse,
)
async def get_department(
    dept_id: int,
    session: AsyncSession = Depends(get_session),
):
    """获取科室详情"""
    department = await session.get(Department, dept_id)
    if not department:
        return err(404, "科室不存在")
    
    return ok(
        DepartmentOut(
            deptId=department.dept_id,
            deptName=department.dept_name,
            deptDesc=department.description,
            parentId=department.parent_id,
            sortOrder=department.sort_order,
            createdAt=department.created_at,
            updatedAt=department.updated_at,
        )
    )


@router.put(
    "/departments/{dept_id}",
    summary="更新科室",
    description="更新科室信息",
    response_model=DepartmentResponse,
)
async def update_department(
    dept_id: int,
    payload: DepartmentUpdate,
    session: AsyncSession = Depends(get_session),
):
    """更新科室"""
    department = await session.get(Department, dept_id)
    if not department:
        return err(404, "科室不存在")
    
    # 检查科室名称是否已存在（排除当前科室）
    if payload.deptName and payload.deptName != department.dept_name:
        exists_stmt = select(Department).where(
            (Department.dept_name == payload.deptName) & (Department.dept_id != dept_id)
        )
        exists_res = await session.execute(exists_stmt)
        if exists_res.scalars().first():
            return err(400, "科室名称已存在")
    
    # 更新字段
    if payload.deptName is not None:
        department.dept_name = payload.deptName
    if payload.deptDesc is not None:
        department.description = payload.deptDesc
    if payload.parentId is not None:
        department.parent_id = payload.parentId
    if payload.sortOrder is not None:
        department.sort_order = payload.sortOrder
    
    department.updated_at = datetime.now()
    await session.commit()
    
    return ok(
            DepartmentOut(
                deptId=department.dept_id,
                deptName=department.dept_name,
                deptDesc=department.description,
                parentId=department.parent_id,
                sortOrder=department.sort_order,
                createdAt=department.created_at,
                updatedAt=department.updated_at,
            ),
            "科室更新成功"
        )


@router.delete(
    "/departments/{dept_id}",
    summary="删除科室",
    description="删除科室信息",
    response_model=DeleteResponse,
)
async def delete_department(
    dept_id: int,
    session: AsyncSession = Depends(get_session),
):
    """删除科室"""
    department = await session.get(Department, dept_id)
    if not department:
        return err(404, "科室不存在")
    
    # 检查是否有子科室
    child_stmt = select(Department).where(Department.parent_id == dept_id)
    child_res = await session.execute(child_stmt)
    if child_res.scalars().first():
        return err(400, "该科室下有子科室，无法删除")
    
    # 检查是否有医生关联
    from app.models.appointment import Doctor
    doctor_stmt = select(Doctor).where(Doctor.dept_id == dept_id)
    doctor_res = await session.execute(doctor_stmt)
    if doctor_res.scalars().first():
        return err(400, "该科室下有医生，无法删除")
    
    await session.delete(department)
    await session.commit()
    
    return ok({"deptId": dept_id}, "科室删除成功")
