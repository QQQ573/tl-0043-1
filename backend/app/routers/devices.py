from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional, List
from datetime import datetime

from ..database import get_db
from .. import models, schemas
from ..validators import is_mainstream_brand, validate_imei, normalize_imei

router = APIRouter(prefix="/devices", tags=["设备档案"])

CURRENT_USER = "admin"


@router.get("", response_model=schemas.PaginatedResponse, summary="分页查询设备列表")
def get_devices(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    brand: Optional[str] = Query(None, description="品牌筛选"),
    appearance_min: Optional[str] = Query(None, description="最低成色"),
    appearance_max: Optional[str] = Query(None, description="最高成色"),
    keyword: Optional[str] = Query(None, description="关键词搜索(型号/IMEI)"),
    db: Session = Depends(get_db),
):
    APPEARANCE_ORDER = ["全新", "99新", "95新", "9成新", "8成新", "7成新及以下"]

    query = db.query(models.Device).filter(models.Device.is_deleted == False)

    if brand:
        query = query.filter(models.Device.brand == brand)

    if keyword:
        like_pattern = f"%{keyword}%"
        query = query.filter(
            models.Device.model.like(like_pattern) |
            models.Device.imei.like(like_pattern)
        )

    if appearance_min and appearance_min in APPEARANCE_ORDER:
        min_idx = APPEARANCE_ORDER.index(appearance_min)
        query = query.filter(
            models.Device.appearance.in_(APPEARANCE_ORDER[:min_idx + 1])
        )

    if appearance_max and appearance_max in APPEARANCE_ORDER:
        max_idx = APPEARANCE_ORDER.index(appearance_max)
        query = query.filter(
            models.Device.appearance.in_(APPEARANCE_ORDER[max_idx:])
        )

    total = query.count()

    items = (
        query
        .order_by(models.Device.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    device_ids = [d.id for d in items]
    inspection_counts = {}
    transaction_counts = {}
    if device_ids:
        ins_counts = (
            db.query(
                models.Inspection.device_id,
                func.count(models.Inspection.id)
            )
            .filter(
                models.Inspection.device_id.in_(device_ids),
                models.Inspection.is_deleted == False
            )
            .group_by(models.Inspection.device_id)
            .all()
        )
        inspection_counts = {device_id: cnt for device_id, cnt in ins_counts}

        trans_counts = (
            db.query(
                models.Transaction.device_id,
                func.count(models.Transaction.id)
            )
            .filter(
                models.Transaction.device_id.in_(device_ids),
                models.Transaction.is_deleted == False
            )
            .group_by(models.Transaction.device_id)
            .all()
        )
        transaction_counts = {device_id: cnt for device_id, cnt in trans_counts}

    result_items = []
    for d in items:
        item_dict = {c.name: getattr(d, c.name) for c in d.__table__.columns}
        item_dict["inspection_count"] = inspection_counts.get(d.id, 0)
        item_dict["transaction_count"] = transaction_counts.get(d.id, 0)
        result_items.append(schemas.DeviceListItem.model_validate(item_dict))

    pages = (total + page_size - 1) // page_size if page_size > 0 else 0

    return schemas.PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        items=result_items,
    )


@router.get("/{device_id}", response_model=schemas.Device, summary="获取设备详情")
def get_device(device_id: int, db: Session = Depends(get_db)):
    device = (
        db.query(models.Device)
        .filter(
            models.Device.id == device_id,
            models.Device.is_deleted == False,
        )
        .first()
    )
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    device.inspections = [
        ins for ins in device.inspections if not ins.is_deleted
    ]
    device.transactions = [
        trans for trans in device.transactions if not trans.is_deleted
    ]
    return device


@router.post("", response_model=schemas.Device, status_code=201, summary="创建设备档案")
def create_device(device_in: schemas.DeviceCreate, db: Session = Depends(get_db)):
    if device_in.imei:
        existing = (
            db.query(models.Device)
            .filter(
                models.Device.imei == device_in.imei,
                models.Device.is_deleted == False,
            )
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="该 IMEI 已存在")

    device = models.Device(**device_in.model_dump())
    device.created_by = CURRENT_USER
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


@router.put("/{device_id}", response_model=schemas.Device, summary="更新设备档案")
def update_device(
    device_id: int,
    device_in: schemas.DeviceUpdate,
    db: Session = Depends(get_db),
):
    device = (
        db.query(models.Device)
        .filter(
            models.Device.id == device_id,
            models.Device.is_deleted == False,
        )
        .first()
    )
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    update_data = device_in.model_dump(exclude_unset=True)

    if "imei" in update_data and update_data["imei"] is not None:
        brand = update_data.get("brand") or device.brand
        if is_mainstream_brand(brand):
            if not validate_imei(update_data["imei"]):
                raise HTTPException(status_code=400, detail="IMEI 格式无效")
        update_data["imei"] = normalize_imei(update_data["imei"])

        if update_data["imei"] != device.imei:
            existing = (
                db.query(models.Device)
                .filter(
                    models.Device.imei == update_data["imei"],
                    models.Device.is_deleted == False,
                    models.Device.id != device_id,
                )
                .first()
            )
            if existing:
                raise HTTPException(status_code=400, detail="该 IMEI 已存在")
    elif "brand" in update_data and is_mainstream_brand(update_data["brand"]):
        if not device.imei:
            raise HTTPException(
                status_code=400,
                detail=f"{update_data['brand']} 为主流品牌，IMEI 为必填项",
            )

    for key, value in update_data.items():
        setattr(device, key, value)

    device.updated_by = CURRENT_USER
    device.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(device)
    return device


@router.delete("/{device_id}", summary="软删除设备档案")
def delete_device(device_id: int, db: Session = Depends(get_db)):
    device = (
        db.query(models.Device)
        .filter(
            models.Device.id == device_id,
            models.Device.is_deleted == False,
        )
        .first()
    )
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    device.is_deleted = True
    device.deleted_at = datetime.utcnow()
    device.deleted_by = CURRENT_USER

    for ins in device.inspections:
        if not ins.is_deleted:
            ins.is_deleted = True
            ins.deleted_at = datetime.utcnow()
            ins.deleted_by = CURRENT_USER

    for trans in device.transactions:
        if not trans.is_deleted:
            trans.is_deleted = True
            trans.deleted_at = datetime.utcnow()
            trans.deleted_by = CURRENT_USER

    db.commit()
    return {"message": "删除成功", "id": device_id}
