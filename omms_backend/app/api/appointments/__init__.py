from fastapi import APIRouter
from app.api.appointments.departments import router as departments_router
from app.api.appointments.doctors import router as doctors_router
from app.api.appointments.schedules import router as schedules_router
from app.api.appointments.appointments import router as appointments_router

router = APIRouter(tags=["appointment"])

# 注册所有路由
router.include_router(departments_router, prefix="", tags=["departments"])
router.include_router(doctors_router, prefix="", tags=["doctors"])
router.include_router(schedules_router, prefix="", tags=["schedules"])
router.include_router(appointments_router, prefix="", tags=["appointments"])
