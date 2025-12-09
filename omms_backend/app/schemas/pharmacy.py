from typing import Optional, List
from pydantic import BaseModel, Field


class MedicineOut(BaseModel):
    id: int = Field(..., description="药品ID")
    name: str = Field(..., description="药品名称")
    specification: Optional[str] = Field(None, description="规格")
    unit: Optional[str] = Field(None, description="单位")
    price: float = Field(..., description="单价")
    warningStock: int = Field(..., description="预警库存")
    currentStock: int = Field(..., description="当前库存")

    model_config = {
        "json_schema_extra": {
            "examples": [{"id": 101, "name": "对乙酰氨基酚片", "specification": "0.5g*20片/盒", "unit": "盒", "price": 12.0, "warningStock": 50, "currentStock": 120}]
        }
    }


class InventoryBatchOut(BaseModel):
    id: int = Field(..., description="批次ID")
    batchNo: str = Field(..., description="批次号")
    medicineId: int = Field(..., description="药品ID")
    medicine: Optional[str] = Field(None, description="药品名称")
    specification: Optional[str] = Field(None, description="规格")
    quantity: int = Field(..., description="数量")
    receivedAt: str = Field(..., description="入库日期")
    expiryDate: Optional[str] = Field(None, description="效期")


class InventoryLogOut(BaseModel):
    id: int = Field(..., description="日志ID")
    type: str = Field(..., description="类型 in/out")
    medicineId: int = Field(..., description="药品ID")
    medicine: Optional[str] = Field(None, description="药品名称")
    specification: Optional[str] = Field(None, description="规格")
    quantity: int = Field(..., description="数量")
    time: str = Field(..., description="时间")
    note: Optional[str] = Field(None, description="备注")


class PrescriptionItemOut(BaseModel):
    medicineId: int = Field(..., description="药品ID")
    name: Optional[str] = Field(None, description="药品名称")
    qty: int = Field(..., description="数量")
    unit: Optional[str] = Field(None, description="单位")
    price: float = Field(..., description="单价")


class PrescriptionOut(BaseModel):
    id: str = Field(..., description="处方号")
    patient: str = Field(..., description="患者")
    department: str = Field(..., description="科室")
    doctor: str = Field(..., description="医生")
    createdAt: str = Field(..., description="创建时间")
    status: str = Field(..., description="状态")
    items: List[PrescriptionItemOut] = Field(default_factory=list, description="处方明细")


class SupplierOut(BaseModel):
    id: int = Field(..., description="供应商ID")
    name: str = Field(..., description="供应商名称")
    contact: Optional[str] = Field(None, description="联系人")
    phone: Optional[str] = Field(None, description="联系电话")
    address: Optional[str] = Field(None, description="地址")


class SupplierOrderItemOut(BaseModel):
    medicineId: int = Field(..., description="药品ID")
    name: Optional[str] = Field(None, description="药品名称")
    qty: int = Field(..., description="数量")
    unit: Optional[str] = Field(None, description="单位")
    price: Optional[float] = Field(None, description="价格")


class SupplierOrderOut(BaseModel):
    id: str = Field(..., description="订单号")
    supplierId: int = Field(..., description="供应商ID")
    createdAt: str = Field(..., description="创建时间")
    status: str = Field(..., description="状态")
    amount: float = Field(..., description="金额")
    items: List[SupplierOrderItemOut] = Field(default_factory=list, description="订单明细")


class InventoryInPayload(BaseModel):
    medicineId: int = Field(..., description="药品ID")
    batchNo: str = Field(..., description="批次号")
    quantity: int = Field(..., description="数量")
    receivedAt: str = Field(..., description="入库日期 YYYY-MM-DD")
    expiryDate: Optional[str] = Field(None, description="效期 YYYY-MM-DD")
    note: Optional[str] = Field(None, description="备注")


class InventoryOutPayload(BaseModel):
    medicineId: int = Field(..., description="药品ID")
    quantity: int = Field(..., description="数量")
    time: Optional[str] = Field(None, description="时间 YYYY-MM-DD HH:MM:SS")
    note: Optional[str] = Field(None, description="备注")


class UpdatePrescriptionStatusPayload(BaseModel):
    status: str = Field(..., description="目标状态 approved/dispensed")


class CreateSupplierPayload(BaseModel):
    name: str = Field(..., description="供应商名称")
    contact: Optional[str] = Field(None, description="联系人")
    phone: Optional[str] = Field(None, description="联系电话")
    address: Optional[str] = Field(None, description="地址")


class CreateOrderItem(BaseModel):
    medicineId: int = Field(..., description="药品ID")
    qty: int = Field(..., description="数量")
    unit: Optional[str] = Field(None, description="单位")
    price: Optional[float] = Field(None, description="单价")


class CreateOrderPayload(BaseModel):
    supplierId: int = Field(..., description="供应商ID")
    items: List[CreateOrderItem] = Field(..., description="订单明细")


class UpdateOrderStatusPayload(BaseModel):
    status: str = Field(..., description="订单状态 completed/cancelled")

