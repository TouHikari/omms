from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class DepartmentCreate(BaseModel):
    """创建科室请求模型"""
    deptName: str = Field(description="科室名称")
    deptDesc: Optional[str] = Field(default=None, description="科室描述")
    parentId: Optional[int] = Field(default=None, description="父级科室ID")
    sortOrder: Optional[int] = Field(default=0, description="排序顺序")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "deptName": "内科",
                    "deptDesc": "内科疾病诊疗",
                    "parentId": None,
                    "sortOrder": 1
                }
            ]
        }
    }


class DepartmentUpdate(BaseModel):
    """更新科室请求模型"""
    deptName: Optional[str] = Field(default=None, description="科室名称")
    deptDesc: Optional[str] = Field(default=None, description="科室描述")
    parentId: Optional[int] = Field(default=None, description="父级科室ID")
    sortOrder: Optional[int] = Field(default=None, description="排序顺序")


class DepartmentOut(BaseModel):
    """科室信息响应模型"""
    deptId: int
    deptName: str
    deptDesc: Optional[str]
    parentId: Optional[int]
    sortOrder: int
    createdAt: Optional[datetime]
    updatedAt: Optional[datetime]
    
    model_config = {
        "from_attributes": True
    }


class DoctorCreate(BaseModel):
    """创建医生请求模型"""
    doctorName: str = Field(description="医生姓名")
    deptId: int = Field(description="所属科室ID")
    userId: int = Field(description="关联用户ID")
    title: Optional[str] = Field(default=None, description="职称")
    specialty: Optional[str] = Field(default=None, description="专业特长")
    introduction: Optional[str] = Field(default=None, description="医生介绍")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "doctorName": "张医生",
                    "deptId": 1,
                    "userId": 1,
                    "title": "主任医师",
                    "specialty": "心血管疾病",
                    "introduction": "擅长心血管疾病的诊断和治疗"
                }
            ]
        }
    }


class DoctorUpdate(BaseModel):
    """更新医生请求模型"""
    doctorName: Optional[str] = Field(default=None, description="医生姓名")
    deptId: Optional[int] = Field(default=None, description="所属科室ID")
    title: Optional[str] = Field(default=None, description="职称")
    specialty: Optional[str] = Field(default=None, description="专业特长")
    introduction: Optional[str] = Field(default=None, description="医生介绍")


class DoctorOut(BaseModel):
    """医生信息响应模型"""
    doctorId: int
    doctorName: str
    deptId: int
    deptName: Optional[str]
    title: Optional[str]
    specialty: Optional[str]
    introduction: Optional[str]
    createdAt: Optional[datetime]
    updatedAt: Optional[datetime]
    
    model_config = {
        "from_attributes": True
    }


class ScheduleOut(BaseModel):
    """排班信息响应模型"""
    scheduleId: int
    doctorId: int
    doctorName: str
    deptId: int
    deptName: str
    workDate: str
    workPeriod: str
    startTime: str
    endTime: str
    totalQuota: int
    bookedCount: int
    availableQuota: int
    status: int


class AppointmentCreate(BaseModel):
    """创建预约请求模型"""
    patientId: int = Field(description="患者ID")
    doctorId: int = Field(description="医生ID")
    scheduleId: int = Field(description="排班ID")
    apptTime: str = Field(description="预约时间")
    symptomDesc: Optional[str] = Field(default=None, description="症状描述")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "patientId": 1001,
                    "doctorId": 1,
                    "scheduleId": 1,
                    "apptTime": "2024-01-15 09:00:00",
                    "symptomDesc": "发热、咳嗽3天"
                }
            ]
        }
    }


class AppointmentUpdate(BaseModel):
    """更新预约请求模型"""
    apptTime: Optional[str] = Field(default=None, description="预约时间")
    symptomDesc: Optional[str] = Field(default=None, description="症状描述")
    status: Optional[int] = Field(default=None, description="预约状态")


class AppointmentOut(BaseModel):
    """预约信息响应模型"""
    apptId: int
    patientId: int
    patientName: str
    doctorId: int
    doctorName: str
    deptId: int
    deptName: str
    scheduleId: int
    apptTime: str
    status: int
    symptomDesc: Optional[str]
    createdAt: Optional[datetime]
    updatedAt: Optional[datetime]
    
    model_config = {
        "from_attributes": True
    }


# 响应模型
class DepartmentListData(BaseModel):
    list: List[DepartmentOut]
    total: int
    page: int
    pageSize: int


class DepartmentListResponse(BaseModel):
    code: int
    message: str
    data: DepartmentListData


class DepartmentResponse(BaseModel):
    code: int
    message: str
    data: DepartmentOut


class DoctorListData(BaseModel):
    list: List[DoctorOut]
    total: int
    page: int
    pageSize: int


class DoctorListResponse(BaseModel):
    code: int
    message: str
    data: DoctorListData


class DoctorResponse(BaseModel):
    code: int
    message: str
    data: DoctorOut


class ScheduleListData(BaseModel):
    list: List[ScheduleOut]
    total: int
    page: int
    pageSize: int


class ScheduleListResponse(BaseModel):
    code: int
    message: str
    data: ScheduleListData


class AppointmentListData(BaseModel):
    list: List[AppointmentOut]
    total: int
    page: int
    pageSize: int


class AppointmentListResponse(BaseModel):
    code: int
    message: str
    data: AppointmentListData


class AppointmentResponse(BaseModel):
    code: int
    message: str
    data: AppointmentOut


class DeleteResponse(BaseModel):
    code: int
    message: str
    data: dict