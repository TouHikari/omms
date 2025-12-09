from datetime import datetime, date
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.response import ok, err
from app.db.session import get_session
from app.core.auth import require_auth
from app.models.medicine import Medicine
from app.models.inventory import InventoryBatch, InventoryLog, MedicineStock
from app.models.prescription import Prescription, PrescriptionItem
from app.models.supplier import Supplier, SupplierOrder, SupplierOrderItem
from app.schemas.pharmacy import (
    MedicineOut,
    InventoryBatchOut,
    InventoryLogOut,
    PrescriptionOut,
    PrescriptionItemOut,
    SupplierOut,
    SupplierOrderOut,
    SupplierOrderItemOut,
    InventoryInPayload,
    InventoryOutPayload,
    UpdatePrescriptionStatusPayload,
    CreateSupplierPayload,
    CreateOrderPayload,
    UpdateOrderStatusPayload,
)


router = APIRouter(tags=["pharmacy"], dependencies=[Depends(require_auth)])


@router.get(
    "/pharmacy/medicines",
    summary="药品列表查询",
    description="查询药品列表，支持分页与低库存筛选",
)
async def list_medicines(
    lowStockOnly: Optional[bool] = Query(default=False),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Medicine)
    total = int((await session.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one())
    rows = (await session.execute(stmt.order_by(Medicine.medicine_id).offset((page - 1) * pageSize).limit(pageSize))).scalars().all()
    mids = [m.medicine_id for m in rows]
    stock_map = {}
    if mids:
        stocks = (await session.execute(select(MedicineStock).where(MedicineStock.medicine_id.in_(mids)))).scalars().all()
        stock_map = {s.medicine_id: s for s in stocks}
    data = [
        MedicineOut(
            id=m.medicine_id,
            name=m.medicine_name,
            specification=m.specification,
            unit=m.unit,
            price=float(m.price or 0.0),
            warningStock=int(m.warning_stock or 0),
            currentStock=int((stock_map.get(m.medicine_id).current_stock if stock_map.get(m.medicine_id) else 0)),
        )
        for m in rows
    ]
    if lowStockOnly:
        data = [x for x in data if (x.currentStock or 0) <= (x.warningStock or 0)]
    return ok({"list": data, "total": total, "page": page, "pageSize": pageSize})


@router.get(
    "/pharmacy/inventory/batches",
    summary="库存批次列表",
    description="查询库存批次并包含药品名称与规格",
)
async def list_batches(
    expiringInDays: Optional[int] = Query(default=None),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(InventoryBatch)
    if expiringInDays is not None and expiringInDays >= 0:
        today = date.today()
        max_date = date.fromordinal(today.toordinal() + expiringInDays)
        stmt = stmt.where((InventoryBatch.expiry_date >= today) & (InventoryBatch.expiry_date <= max_date))
    rows: List[InventoryBatch] = (await session.execute(stmt.order_by(InventoryBatch.id))).scalars().all()
    # prefetch medicines
    mids = {b.medicine_id for b in rows}
    med_map = {}
    if mids:
        meds = (await session.execute(select(Medicine).where(Medicine.medicine_id.in_(list(mids))))).scalars().all()
        med_map = {m.medicine_id: m for m in meds}
    data = [
        InventoryBatchOut(
            id=b.id,
            batchNo=b.batch_no,
            medicineId=b.medicine_id,
            medicine=med_map.get(b.medicine_id).medicine_name if med_map.get(b.medicine_id) else None,
            specification=med_map.get(b.medicine_id).specification if med_map.get(b.medicine_id) else None,
            quantity=b.quantity,
            receivedAt=b.received_at.strftime("%Y-%m-%d") if b.received_at else None,
            expiryDate=b.expiry_date.strftime("%Y-%m-%d") if b.expiry_date else None,
        )
        for b in rows
    ]
    return ok(data)


@router.get(
    "/pharmacy/inventory/logs",
    summary="入出库日志",
    description="查询入出库日志并包含药品名称",
)
async def list_logs(
    type: Optional[str] = Query(default=None),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(InventoryLog)
    if type in ("in", "out"):
        stmt = stmt.where(InventoryLog.type == type)
    rows: List[InventoryLog] = (await session.execute(stmt.order_by(InventoryLog.id.desc()))).scalars().all()
    # prefetch medicines
    mids = {l.medicine_id for l in rows}
    med_map = {}
    if mids:
        meds = (await session.execute(select(Medicine).where(Medicine.medicine_id.in_(list(mids))))).scalars().all()
        med_map = {m.medicine_id: m for m in meds}
    data = [
        InventoryLogOut(
            id=l.id,
            type=l.type,
            medicineId=l.medicine_id,
            medicine=med_map.get(l.medicine_id).medicine_name if med_map.get(l.medicine_id) else None,
            specification=med_map.get(l.medicine_id).specification if med_map.get(l.medicine_id) else None,
            quantity=l.quantity,
            time=l.time.strftime("%Y-%m-%d %H:%M:%S") if l.time else None,
            note=l.note,
        )
        for l in rows
    ]
    return ok(data)


@router.post(
    "/pharmacy/inventory/in",
    summary="入库",
    description="创建批次与日志，并增加药品库存",
)
async def inventory_in(payload: InventoryInPayload, session: AsyncSession = Depends(get_session)):
    med = (await session.execute(select(Medicine).where(Medicine.medicine_id == payload.medicineId))).scalars().first()
    if not med:
        return err(404, "药品不存在")
    try:
        rec_date = datetime.strptime(payload.receivedAt, "%Y-%m-%d").date()
        exp_date = datetime.strptime(payload.expiryDate, "%Y-%m-%d").date() if payload.expiryDate else None
    except Exception:
        return err(400, "日期格式错误")
    batch = InventoryBatch(
        medicine_id=payload.medicineId,
        batch_no=payload.batchNo,
        quantity=payload.quantity,
        received_at=rec_date,
        expiry_date=exp_date,
    )
    log = InventoryLog(
        type="in",
        medicine_id=payload.medicineId,
        quantity=payload.quantity,
        note=payload.note,
        batch_no=payload.batchNo,
        time=datetime.now(),
    )
    stock = (await session.execute(select(MedicineStock).where(MedicineStock.medicine_id == payload.medicineId))).scalars().first()
    if not stock:
        stock = MedicineStock(medicine_id=payload.medicineId, current_stock=0)
        session.add(stock)
        await session.flush()
    stock.current_stock = int(stock.current_stock or 0) + int(payload.quantity)
    session.add(batch)
    session.add(log)
    await session.commit()
    return ok({"batch": batch.id, "log": log.id, "medicine": med.medicine_id})


@router.post(
    "/pharmacy/inventory/out",
    summary="出库",
    description="写入出库日志并扣减库存",
)
async def inventory_out(payload: InventoryOutPayload, session: AsyncSession = Depends(get_session)):
    med = (await session.execute(select(Medicine).where(Medicine.medicine_id == payload.medicineId))).scalars().first()
    if not med:
        return err(404, "药品不存在")
    qty = payload.quantity
    if qty <= 0:
        return err(400, "数量必须大于0")
    stock = (await session.execute(select(MedicineStock).where(MedicineStock.medicine_id == payload.medicineId))).scalars().first()
    if not stock or (stock.current_stock or 0) < qty:
        return err(400, "库存不足")
    when = datetime.strptime(payload.time, "%Y-%m-%d %H:%M:%S") if payload.time else datetime.now()
    log = InventoryLog(type="out", medicine_id=payload.medicineId, quantity=qty, note=payload.note, time=when)
    stock.current_stock = int(stock.current_stock or 0) - int(qty)
    session.add(log)
    await session.commit()
    return ok({"log": log.id, "medicine": med.medicine_id})


@router.get(
    "/pharmacy/prescriptions",
    summary="处方列表",
    description="查询处方列表，支持按状态筛选",
)
async def list_prescriptions(status: Optional[str] = Query(default=None), session: AsyncSession = Depends(get_session)):
    stmt = select(Prescription).options(selectinload(Prescription.items))
    if status in ("pending", "approved", "dispensed"):
        stmt = stmt.where(Prescription.status == status)
    rows: List[Prescription] = (await session.execute(stmt.order_by(Prescription.created_at.desc()))).scalars().all()
    # fetch items per prescription
    data: List[PrescriptionOut] = []
    for p in rows:
        items: List[PrescriptionItem] = p.items
        data.append(
            PrescriptionOut(
                id=p.id,
                patient=p.patient,
                department=p.department,
                doctor=p.doctor,
                createdAt=p.created_at.strftime("%Y-%m-%d %H:%M:%S") if p.created_at else None,
                status=p.status,
                items=[
                    PrescriptionItemOut(
                        medicineId=i.medicine_id,
                        name=i.name,
                        qty=i.qty,
                        unit=i.unit,
                        price=float(i.price or 0.0),
                    )
                    for i in items
                ],
            )
        )
    return ok(data)


@router.patch(
    "/pharmacy/prescriptions/{pid}/status",
    summary="更新处方状态",
    description="合法流转：pending -> approved -> dispensed；发药会扣减库存并写入出库日志",
)
async def update_prescription_status(pid: str, payload: UpdatePrescriptionStatusPayload, session: AsyncSession = Depends(get_session)):
    p = (await session.execute(select(Prescription).options(selectinload(Prescription.items)).where(Prescription.id == pid))).scalars().first()
    if not p:
        return err(404, "处方不存在")
    prev = p.status
    target = payload.status
    allowed = {"pending": ["approved"], "approved": ["dispensed"], "dispensed": []}
    if target not in allowed.get(prev, []):
        return err(400, "非法状态流转")
    p.status = target
    if target == "dispensed":
        for item in p.items:
            med = (await session.execute(select(Medicine).where(Medicine.medicine_id == item.medicine_id))).scalars().first()
            if not med:
                return err(404, f"药品不存在: {item.medicine_id}")
            stock = (await session.execute(select(MedicineStock).where(MedicineStock.medicine_id == item.medicine_id))).scalars().first()
            if not stock or (stock.current_stock or 0) < item.qty:
                return err(400, f"库存不足: {med.medicine_name}")
            stock.current_stock = int(stock.current_stock or 0) - int(item.qty)
            log = InventoryLog(type="out", medicine_id=item.medicine_id, quantity=item.qty, note=f"处方发药 {pid}", time=datetime.now())
            session.add(log)
    await session.commit()
    return ok({"id": p.id, "status": p.status})


@router.get(
    "/pharmacy/suppliers",
    summary="供应商列表",
    description="查询供应商列表",
)
async def list_suppliers(session: AsyncSession = Depends(get_session)):
    rows: List[Supplier] = (await session.execute(select(Supplier).order_by(Supplier.id))).scalars().all()
    data = [
        SupplierOut(id=s.id, name=s.name, contact=s.contact, phone=s.phone, address=s.address)
        for s in rows
    ]
    return ok(data)


@router.post(
    "/pharmacy/suppliers",
    summary="创建供应商",
    description="创建供应商信息",
)
async def create_supplier(payload: CreateSupplierPayload, session: AsyncSession = Depends(get_session)):
    name = payload.name.strip()
    if not name:
        return err(400, "供应商名称不能为空")
    s = Supplier(name=name, contact=(payload.contact or "").strip() or None, phone=(payload.phone or "").strip() or None, address=(payload.address or "").strip() or None)
    session.add(s)
    await session.commit()
    await session.refresh(s)
    return ok(SupplierOut(id=s.id, name=s.name, contact=s.contact, phone=s.phone, address=s.address), "供应商创建成功")


@router.get(
    "/pharmacy/orders",
    summary="采购订单列表",
    description="查询采购订单列表",
)
async def list_orders(status: Optional[str] = Query(default=None), session: AsyncSession = Depends(get_session)):
    stmt = select(SupplierOrder).options(selectinload(SupplierOrder.items))
    if status in ("pending", "completed", "cancelled"):
        stmt = stmt.where(SupplierOrder.status == status)
    orders: List[SupplierOrder] = (await session.execute(stmt.order_by(SupplierOrder.created_at.desc()))).scalars().all()
    data = []
    for o in orders:
        items = [
            SupplierOrderItemOut(medicineId=i.medicine_id, name=i.name, qty=i.qty, unit=i.unit, price=float(i.price or 0.0))
            for i in o.items
        ]
        data.append(
            SupplierOrderOut(
                id=o.id,
                supplierId=o.supplier_id,
                createdAt=o.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                status=o.status,
                amount=float(o.amount or 0.0),
                items=items,
            )
        )
    return ok(data)


@router.post(
    "/pharmacy/orders",
    summary="创建采购订单",
    description="创建订单并计算金额",
)
async def create_order(payload: CreateOrderPayload, session: AsyncSession = Depends(get_session)):
    supplier = await session.get(Supplier, payload.supplierId)
    if not supplier:
        return err(404, "供应商不存在")
    # 生成订单号
    today = datetime.now().strftime("%Y%m%d")
    # 简单序号：使用时间戳后4位
    seq = str(int(datetime.now().timestamp()))[-4:]
    oid = f"PO-{today}-{seq}"
    order = SupplierOrder(id=oid, supplier_id=supplier.id, status="pending", amount=0.0)
    session.add(order)
    await session.flush()
    amount = 0.0
    for it in payload.items:
        med = (await session.execute(select(Medicine).where(Medicine.medicine_id == it.medicineId))).scalars().first()
        if not med:
            return err(404, f"药品不存在: {it.medicineId}")
        price = float(it.price if it.price is not None else float(med.price or 0.0))
        item = SupplierOrderItem(order_id=order.id, medicine_id=it.medicineId, name=med.medicine_name, qty=it.qty, unit=it.unit or med.unit, price=price)
        session.add(item)
        amount += price * it.qty
    order.amount = amount
    await session.commit()
    await session.refresh(order)
    return ok({"id": order.id, "amount": float(order.amount)})


@router.patch(
    "/pharmacy/orders/{oid}/status",
    summary="更新订单状态",
    description="completed 会执行入库流程，cancelled 仅修改状态",
)
async def update_order_status(oid: str, payload: UpdateOrderStatusPayload, session: AsyncSession = Depends(get_session)):
    order = (await session.execute(select(SupplierOrder).options(selectinload(SupplierOrder.items)).where(SupplierOrder.id == oid))).scalars().first()
    if not order:
        return err(404, "订单不存在")
    if payload.status not in ("completed", "cancelled"):
        return err(400, "非法状态")
    if order.status != "pending":
        return err(400, "订单不可更新")
    order.status = payload.status
    if payload.status == "completed":
        # 将订单项入库并写日志
        for it in order.items:
            med = (await session.execute(select(Medicine).where(Medicine.medicine_id == it.medicine_id))).scalars().first()
            if not med:
                return err(404, f"药品不存在: {it.medicine_id}")
            batch_no = f"B-{oid}-{it.medicine_id}"
            batch = InventoryBatch(medicine_id=it.medicine_id, batch_no=batch_no, quantity=it.qty, received_at=date.today())
            log = InventoryLog(type="in", medicine_id=it.medicine_id, quantity=it.qty, note=f"订单入库 {oid}", batch_no=batch_no, time=datetime.now())
            stock = (await session.execute(select(MedicineStock).where(MedicineStock.medicine_id == it.medicine_id))).scalars().first()
            if not stock:
                stock = MedicineStock(medicine_id=it.medicine_id, current_stock=0)
                session.add(stock)
                await session.flush()
            stock.current_stock = int(stock.current_stock or 0) + int(it.qty)
            session.add(batch)
            session.add(log)
    await session.commit()
    return ok({"id": order.id, "status": order.status})
