from typing import List, Optional

from pydantic import BaseModel, Field


class RecordCreate(BaseModel):
    deptId: int = Field(description="科室ID")
    doctorId: int = Field(description="医生ID")
    patientId: Optional[int] = Field(default=None, description="患者ID")
    patientName: Optional[str] = Field(default=None, description="患者姓名，仅在缺少ID时记录")
    time: Optional[str] = Field(default=None, description="就诊时间，格式 HH:mm，默认 10:00")
    chiefComplaint: Optional[str] = Field(default=None, description="主诉")
    diagnosis: Optional[str] = Field(default=None, description="诊断")
    prescriptions: Optional[List[str]] = Field(default=None, description="处方项目")
    labs: Optional[List[str]] = Field(default=None, description="检验项目")
    imaging: Optional[List[str]] = Field(default=None, description="影像项目")
    templateId: Optional[int] = Field(default=None, description="使用的模板ID")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "deptId": 1,
                    "doctorId": 1,
                    "patientId": 10086,
                    "time": "10:00",
                    "chiefComplaint": "发热伴咳嗽3天",
                    "diagnosis": "上呼吸道感染？",
                    "prescriptions": ["对乙酰氨基酚"],
                    "labs": ["血常规"],
                    "imaging": ["胸片"],
                }
            ]
        }
    }


class RecordUpdate(BaseModel):
    patientId: Optional[int] = Field(default=None, description="患者ID")
    patientName: Optional[str] = Field(default=None, description="患者姓名")
    chiefComplaint: Optional[str] = Field(default=None, description="主诉")
    diagnosis: Optional[str] = Field(default=None, description="诊断")
    prescriptions: Optional[List[str]] = Field(default=None, description="处方项目")
    labs: Optional[List[str]] = Field(default=None, description="检验项目")
    imaging: Optional[List[str]] = Field(default=None, description="影像项目")
    createdAt: Optional[str] = Field(default=None, description="创建时间，格式 YYYY-MM-DD HH:mm")
    deptId: Optional[int] = Field(default=None, description="科室ID")
    doctorId: Optional[int] = Field(default=None, description="医生ID")


class TemplateCreate(BaseModel):
    name: str = Field(description="模板名称")
    scope: Optional[str] = Field(default="通用", description="适用范围")
    fields: Optional[List[str]] = Field(default=None, description="模板字段集合")
    defaults: Optional[dict] = Field(default=None, description="默认值对象")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "内科常用模板",
                    "scope": "内科",
                    "fields": ["chiefComplaint", "diagnosis", "prescriptions"],
                    "defaults": {
                        "chiefComplaint": "主诉：",
                        "diagnosis": "初步诊断：",
                        "prescriptions": ["口服药物"],
                        "labs": ["血常规"],
                        "imaging": []
                    }
                }
            ]
        }
    }


class TemplateUpdate(BaseModel):
    name: Optional[str] = Field(default=None, description="模板名称")
    scope: Optional[str] = Field(default=None, description="适用范围")
    fields: Optional[List[str]] = Field(default=None, description="模板字段集合")
    defaults: Optional[dict] = Field(default=None, description="默认值对象")


class MedicalRecordOut(BaseModel):
    id: str
    patient: str
    department: str
    doctor: str
    createdAt: str
    status: str
    hasLab: bool
    hasImaging: bool
    chiefComplaint: str
    diagnosis: str
    prescriptions: List[str]
    labs: List[str]
    imaging: List[str]


class RecordsListData(BaseModel):
    list: List[MedicalRecordOut]
    total: int
    page: int
    pageSize: int


class RecordsListResponse(BaseModel):
    code: int
    message: str
    data: Optional[RecordsListData]


class RecordResponse(BaseModel):
    code: int
    message: str
    data: Optional[MedicalRecordOut]


class RecordStatusData(BaseModel):
    id: str
    status: str


class RecordStatusResponse(BaseModel):
    code: int
    message: str
    data: Optional[RecordStatusData]


class DeleteRecordResponse(BaseModel):
    code: int
    message: str
    data: Optional[RecordStatusData]


class RecordTemplateOut(BaseModel):
    id: int
    name: str
    scope: str
    fields: List[str]
    defaults: dict


class RecordTemplateListResponse(BaseModel):
    code: int
    message: str
    data: Optional[List[RecordTemplateOut]]


class RecordTemplateResponse(BaseModel):
    code: int
    message: str
    data: Optional[RecordTemplateOut]


class TemplateDeleteResponse(BaseModel):
    code: int
    message: str
    data: Optional[dict]
