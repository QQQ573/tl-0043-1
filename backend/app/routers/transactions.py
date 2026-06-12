import statistics
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime, timedelta

from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/transactions", tags=["成交记录"])

CURRENT_USER = "admin"


@router.get("", response_model=list[schemas.Transaction], summary="查询成交记录列表")
def get_transactions(
    device_id: Optional[int] = Query(None, description="设备ID筛选"),
    trade_type: Optional[str] = Query(None, description="交易类型筛选"),
    db: Session = Depends(get_db),
):
    query = db.query(models.Transaction).filter(models.Transaction.is_deleted == False)

    if device_id:
        query = query.filter(models.Transaction.device_id == device_id)

    if trade_type:
        query = query.filter(models.Transaction.trade_type == trade_type)

    return query.order_by(models.Transaction.trade_date.desc()).all()


@router.get("/stats/benchmark", response_model=schemas.BenchmarkResponse, summary="同款成交行情基准")
def get_benchmark(
    brand: str = Query(..., description="品牌"),
    model: str = Query(..., description="型号"),
    appearance: Optional[str] = Query(None, description="成色筛选"),
    days: int = Query(90, ge=1, le=365, description="近N天"),
    db: Session = Depends(get_db),
):
    cutoff_date = datetime.utcnow().date() - timedelta(days=days)

    query = (
        db.query(models.Transaction.actual_amount)
        .join(models.Device, models.Transaction.device_id == models.Device.id)
        .filter(
            models.Transaction.is_deleted == False,
            models.Device.is_deleted == False,
            models.Device.brand == brand,
            models.Device.model == model,
            models.Transaction.trade_date >= cutoff_date,
        )
    )

    if appearance:
        query = query.filter(models.Device.appearance == appearance)

    amounts = [row[0] for row in query.all()]

    if not amounts:
        return schemas.BenchmarkResponse(
            brand=brand,
            model=model,
            appearance=appearance,
            days=days,
            count=0,
            max_price=None,
            min_price=None,
            avg_price=None,
            median_price=None,
        )

    sorted_amounts = sorted(amounts)
    return schemas.BenchmarkResponse(
        brand=brand,
        model=model,
        appearance=appearance,
        days=days,
        count=len(amounts),
        max_price=max(amounts),
        min_price=min(amounts),
        avg_price=round(statistics.mean(amounts), 2),
        median_price=round(statistics.median(amounts), 2),
    )


@router.get("/{transaction_id}", response_model=schemas.Transaction, summary="获取成交记录详情")
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = (
        db.query(models.Transaction)
        .filter(
            models.Transaction.id == transaction_id,
            models.Transaction.is_deleted == False,
        )
        .first()
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="成交记录不存在")
    return transaction


@router.post("", response_model=schemas.Transaction, status_code=201, summary="创建成交记录")
def create_transaction(transaction_in: schemas.TransactionCreate, db: Session = Depends(get_db)):
    device = (
        db.query(models.Device)
        .filter(
            models.Device.id == transaction_in.device_id,
            models.Device.is_deleted == False,
        )
        .first()
    )
    if not device:
        raise HTTPException(status_code=404, detail="关联的设备不存在")

    transaction = models.Transaction(**transaction_in.model_dump())
    transaction.created_by = CURRENT_USER
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    if transaction_in.trade_type == "转售" and device.status == "在库待售":
        device.status = "已售出"
        device.updated_by = CURRENT_USER
        device.updated_at = datetime.utcnow()
        db.commit()

    return transaction


@router.put("/{transaction_id}", response_model=schemas.Transaction, summary="更新成交记录")
def update_transaction(
    transaction_id: int,
    transaction_in: schemas.TransactionUpdate,
    db: Session = Depends(get_db),
):
    transaction = (
        db.query(models.Transaction)
        .filter(
            models.Transaction.id == transaction_id,
            models.Transaction.is_deleted == False,
        )
        .first()
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="成交记录不存在")

    update_data = transaction_in.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(transaction, key, value)

    transaction.updated_by = CURRENT_USER
    transaction.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(transaction)
    return transaction


@router.delete("/{transaction_id}", summary="软删除成交记录")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = (
        db.query(models.Transaction)
        .filter(
            models.Transaction.id == transaction_id,
            models.Transaction.is_deleted == False,
        )
        .first()
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="成交记录不存在")

    transaction.is_deleted = True
    transaction.deleted_at = datetime.utcnow()
    transaction.deleted_by = CURRENT_USER
    db.commit()
    return {"message": "删除成功", "id": transaction_id}
