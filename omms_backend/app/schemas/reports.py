from typing import List, Optional

from pydantic import BaseModel, Field


class DailyVisitItem(BaseModel):
    id: str = Field(description="业务ID显示，如 R-YYYYMMDD-XXXX")
    patient: str = Field(description="患者姓名")
    department: str = Field(description="科室名称")
    doctor: str = Field(description="医生姓名")
    time: str = Field(description="就诊时间，YYYY-MM-DD HH:mm:ss")
    status: str = Field(description="状态，pending|completed|cancelled")


class DailyVisitsData(BaseModel):
    list: List[DailyVisitItem]
    total: int


class DailyVisitsResponse(BaseModel):
    code: int
    message: str
    data: Optional[DailyVisitsData]


class DailyDrugItem(BaseModel):
    id: str = Field(description="行唯一ID，如 rxId-itemId")
    medicine: str = Field(description="药品名称")
    specification: Optional[str] = Field(default=None, description="规格")
    quantity: int = Field(description="数量")
    patient: str = Field(description="患者姓名")
    department: str = Field(description="科室名称")
    doctor: str = Field(description="医生姓名")
    date: str = Field(description="日期，YYYY-MM-DD")


class DailyDrugsData(BaseModel):
    list: List[DailyDrugItem]
    total: int


class DailyDrugsResponse(BaseModel):
    code: int
    message: str
    data: Optional[DailyDrugsData]


class MonthlyVisitItem(BaseModel):
    date: str = Field(description="日期，YYYY-MM-DD")
    count: int = Field(description="当日就诊数量")


class MonthlyVisitsData(BaseModel):
    list: List[MonthlyVisitItem]
    totalDays: int


class MonthlyVisitsResponse(BaseModel):
    code: int
    message: str
    data: Optional[MonthlyVisitsData]


class MonthlyDrugItem(BaseModel):
    date: str = Field(description="日期，YYYY-MM-DD")
    items: int = Field(description="当日药品项数（处方条目数总和）")


class MonthlyDrugsData(BaseModel):
    list: List[MonthlyDrugItem]
    totalDays: int


class MonthlyDrugsResponse(BaseModel):
    code: int
    message: str
    data: Optional[MonthlyDrugsData]


class CustomReportRow(BaseModel):
    patient: str
    department: str
    doctor: str
    time: str
    status: str
    drugItems: int


class CustomReportData(BaseModel):
    list: List[CustomReportRow]
    total: int


class CustomReportResponse(BaseModel):
    code: int
    message: str
    data: Optional[CustomReportData]

