from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/inspections", tags=["质检记录"])

CURRENT_USER = "admin"


@router.get("", response_model=list[schemas.Inspection], summary="查询质检记录列表")
def get_inspections(
    device_id: Optional[int] = Query(None, description="设备ID筛选"),
    db: Session = Depends(get_db),
):
    query = db.query(models.Inspection).filter(models.Inspection.is_deleted == False)

    if device_id:
        query = query.filter(models.Inspection.device_id == device_id)

    return query.order_by(models.Inspection.inspection_date.desc()).all()


@router.get("/{inspection_id}", response_model=schemas.Inspection, summary="获取质检记录详情")
def get_inspection(inspection_id: int, db: Session = Depends(get_db)):
    inspection = (
        db.query(models.Inspection)
        .filter(
            models.Inspection.id == inspection_id,
            models.Inspection.is_deleted == False,
        )
        .first()
    )
    if not inspection:
        raise HTTPException(status_code=404, detail="质检记录不存在")
    return inspection


@router.post("", response_model=schemas.Inspection, status_code=201, summary="创建质检记录")
def create_inspection(inspection_in: schemas.InspectionCreate, db: Session = Depends(get_db)):
    device = (
        db.query(models.Device)
        .filter(
            models.Device.id == inspection_in.device_id,
            models.Device.is_deleted == False,
        )
        .first()
    )
    if not device:
        raise HTTPException(status_code=404, detail="关联的设备不存在")

    inspection = models.Inspection(**inspection_in.model_dump())
    inspection.created_by = CURRENT_USER
    db.add(inspection)
    db.commit()
    db.refresh(inspection)
    return inspection


@router.put("/{inspection_id}", response_model=schemas.Inspection, summary="更新质检记录")
def update_inspection(
    inspection_id: int,
    inspection_in: schemas.InspectionUpdate,
    db: Session = Depends(get_db),
):
    inspection = (
        db.query(models.Inspection)
        .filter(
            models.Inspection.id == inspection_id,
            models.Inspection.is_deleted == False,
        )
        .first()
    )
    if not inspection:
        raise HTTPException(status_code=404, detail="质检记录不存在")

    update_data = inspection_in.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(inspection, key, value)

    inspection.updated_by = CURRENT_USER
    inspection.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(inspection)
    return inspection


@router.delete("/{inspection_id}", summary="软删除质检记录")
def delete_inspection(inspection_id: int, db: Session = Depends(get_db)):
    inspection = (
        db.query(models.Inspection)
        .filter(
            models.Inspection.id == inspection_id,
            models.Inspection.is_deleted == False,
        )
        .first()
    )
    if not inspection:
        raise HTTPException(status_code=404, detail="质检记录不存在")

    inspection.is_deleted = True
    inspection.deleted_at = datetime.utcnow()
    inspection.deleted_by = CURRENT_USER
    db.commit()
    return {"message": "删除成功", "id": inspection_id}
