import os
import sys
import tempfile
import statistics
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app import models

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def setup_module():
    db = TestingSessionLocal()
    try:
        db.query(models.Transaction).delete()
        db.query(models.Inspection).delete()
        db.query(models.Device).delete()
        db.commit()
    finally:
        db.close()


def test_benchmark_empty_sample():
    """测试用例 1：空样本 — 没有任何成交记录时返回 count=0 且价格字段为 None"""
    response = client.get(
        "/api/v1/transactions/stats/benchmark",
        params={
            "brand": "苹果",
            "model": "iPhone 15 Pro",
            "days": 90,
        },
    )
    assert response.status_code == 200, f"期望 200，实际 {response.status_code}"
    data = response.json()
    assert data["brand"] == "苹果"
    assert data["model"] == "iPhone 15 Pro"
    assert data["days"] == 90
    assert data["appearance"] is None
    assert data["count"] == 0
    assert data["max_price"] is None
    assert data["min_price"] is None
    assert data["avg_price"] is None
    assert data["median_price"] is None
    print("[PASS] test_benchmark_empty_sample - 空样本测试通过")


def test_benchmark_single_transaction():
    """测试用例 2：单笔成交 — 仅一条记录时，最高/最低/均价/中位价应一致"""
    db = TestingSessionLocal()
    try:
        device = models.Device(
            brand="华为",
            model="Mate 60 Pro",
            imei="860123456789012",
            appearance="95新",
            storage="256GB",
            estimated_price=5000.0,
            status="在库待售",
        )
        db.add(device)
        db.flush()

        today = date.today()
        tx = models.Transaction(
            device_id=device.id,
            trade_type="转售",
            actual_amount=5200.0,
            counterparty_name="张三",
            trade_date=today,
            settlement_method="转账",
        )
        db.add(tx)
        db.commit()

        response = client.get(
            "/api/v1/transactions/stats/benchmark",
            params={
                "brand": "华为",
                "model": "Mate 60 Pro",
                "days": 30,
            },
        )
        assert response.status_code == 200, f"期望 200，实际 {response.status_code}"
        data = response.json()
        assert data["count"] == 1
        assert data["max_price"] == 5200.0
        assert data["min_price"] == 5200.0
        assert data["avg_price"] == 5200.0
        assert data["median_price"] == 5200.0
        print("[PASS] test_benchmark_single_transaction - 单笔成交测试通过")
    finally:
        db.close()


def test_benchmark_cross_appearance_filter():
    """测试用例 3：跨成色过滤 — 多成色设备存在时，指定成色筛选应只返回对应成色的统计"""
    db = TestingSessionLocal()
    try:
        today = date.today()

        dev1 = models.Device(brand="小米", model="Xiaomi 14", appearance="99新",
                             imei="861111111111111", estimated_price=4000, status="在库待售")
        dev2 = models.Device(brand="小米", model="Xiaomi 14", appearance="95新",
                             imei="862222222222222", estimated_price=3500, status="在库待售")
        dev3 = models.Device(brand="小米", model="Xiaomi 14", appearance="9成新",
                             imei="863333333333333", estimated_price=3000, status="在库待售")
        db.add_all([dev1, dev2, dev3])
        db.flush()

        txs = [
            models.Transaction(device_id=dev1.id, trade_type="转售", actual_amount=4200,
                               counterparty_name="A", trade_date=today, settlement_method="现金"),
            models.Transaction(device_id=dev1.id, trade_type="回收", actual_amount=3800,
                               counterparty_name="B", trade_date=today - timedelta(days=5),
                               settlement_method="转账"),
            models.Transaction(device_id=dev2.id, trade_type="转售", actual_amount=3600,
                               counterparty_name="C", trade_date=today - timedelta(days=3),
                               settlement_method="现金"),
            models.Transaction(device_id=dev2.id, trade_type="转售", actual_amount=3500,
                               counterparty_name="D", trade_date=today - timedelta(days=10),
                               settlement_method="以旧换新抵扣"),
            models.Transaction(device_id=dev3.id, trade_type="转售", actual_amount=3100,
                               counterparty_name="E", trade_date=today - timedelta(days=2),
                               settlement_method="转账"),
        ]
        db.add_all(txs)
        db.commit()

        all_amounts = [4200, 3800, 3600, 3500, 3100]
        response = client.get(
            "/api/v1/transactions/stats/benchmark",
            params={"brand": "小米", "model": "Xiaomi 14", "days": 30},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 5
        assert data["max_price"] == max(all_amounts)
        assert data["min_price"] == min(all_amounts)
        assert data["avg_price"] == round(statistics.mean(all_amounts), 2)
        assert data["median_price"] == round(statistics.median(all_amounts), 2)
        print("[PASS] test_benchmark_cross_appearance_filter - 全量统计通过")

        appearance_amounts = [4200, 3800]
        response_99 = client.get(
            "/api/v1/transactions/stats/benchmark",
            params={"brand": "小米", "model": "Xiaomi 14", "appearance": "99新", "days": 30},
        )
        assert response_99.status_code == 200
        data_99 = response_99.json()
        assert data_99["count"] == 2
        assert data_99["appearance"] == "99新"
        assert data_99["max_price"] == max(appearance_amounts)
        assert data_99["min_price"] == min(appearance_amounts)
        assert data_99["avg_price"] == round(statistics.mean(appearance_amounts), 2)
        assert data_99["median_price"] == round(statistics.median(appearance_amounts), 2)
        print("[PASS] test_benchmark_cross_appearance_filter - 99新筛选通过")

        response_95 = client.get(
            "/api/v1/transactions/stats/benchmark",
            params={"brand": "小米", "model": "Xiaomi 14", "appearance": "95新", "days": 30},
        )
        assert response_95.status_code == 200
        data_95 = response_95.json()
        assert data_95["count"] == 2
        assert data_95["max_price"] == 3600.0
        assert data_95["min_price"] == 3500.0
        print("[PASS] test_benchmark_cross_appearance_filter - 95新筛选通过")

        old_amounts = [3100]
        response_old = client.get(
            "/api/v1/transactions/stats/benchmark",
            params={"brand": "小米", "model": "Xiaomi 14", "appearance": "9成新", "days": 30},
        )
        assert response_old.status_code == 200
        data_old = response_old.json()
        assert data_old["count"] == 1
        assert data_old["max_price"] == 3100.0
        print("[PASS] test_benchmark_cross_appearance_filter - 9成新筛选通过")

        response_none = client.get(
            "/api/v1/transactions/stats/benchmark",
            params={"brand": "小米", "model": "Xiaomi 14", "appearance": "全新", "days": 30},
        )
        assert response_none.status_code == 200
        data_none = response_none.json()
        assert data_none["count"] == 0
        assert data_none["max_price"] is None
        print("[PASS] test_benchmark_cross_appearance_filter - 全新(无数据)筛选通过")

        print("[PASS] test_benchmark_cross_appearance_filter - 跨成色过滤测试通过")
    finally:
        db.close()


def test_transaction_crud():
    """测试成交记录完整 CRUD"""
    db = TestingSessionLocal()
    try:
        device = models.Device(
            brand="三星",
            model="Galaxy S24",
            imei="350123456789012",
            appearance="95新",
            estimated_price=4500.0,
            status="在库待售",
        )
        db.add(device)
        db.commit()
        db.refresh(device)

        response = client.post(
            "/api/v1/transactions",
            json={
                "device_id": device.id,
                "trade_type": "回收",
                "actual_amount": 4200.0,
                "counterparty_name": "李先生",
                "trade_date": date.today().isoformat(),
                "settlement_method": "转账",
                "notes": "测试回收交易",
            },
        )
        print(f"Create response: {response.status_code} {response.text}")
        assert response.status_code == 201, f"期望 201，实际 {response.status_code}: {response.text}"
        tx_id = response.json()["id"]
        assert response.json()["trade_type"] == "回收"
        assert response.json()["actual_amount"] == 4200.0
        print("[PASS] test_transaction_crud - 创建通过")

        response = client.get(f"/api/v1/transactions/{tx_id}")
        assert response.status_code == 200
        assert response.json()["counterparty_name"] == "李先生"
        print("[PASS] test_transaction_crud - 查询通过")

        response = client.put(
            f"/api/v1/transactions/{tx_id}",
            json={"actual_amount": 4300.0, "notes": "价格上调"},
        )
        assert response.status_code == 200
        assert response.json()["actual_amount"] == 4300.0
        assert response.json()["notes"] == "价格上调"
        print("[PASS] test_transaction_crud - 更新通过")

        response = client.get(f"/api/v1/transactions?device_id={device.id}")
        assert response.status_code == 200
        assert len(response.json()) >= 1
        print("[PASS] test_transaction_crud - 列表查询通过")

        response = client.delete(f"/api/v1/transactions/{tx_id}")
        assert response.status_code == 200
        print("[PASS] test_transaction_crud - 删除通过")

        response = client.get(f"/api/v1/transactions/{tx_id}")
        assert response.status_code == 404
        print("[PASS] test_transaction_crud - 软删除验证通过")

        print("[PASS] test_transaction_crud - 完整 CRUD 测试通过")
    finally:
        db.close()


def test_resale_auto_status():
    """测试转售记录自动更新设备状态"""
    db = TestingSessionLocal()
    try:
        device = models.Device(
            brand="OPPO",
            model="Find X7",
            imei="864444444444444",
            appearance="99新",
            estimated_price=3800.0,
            status="在库待售",
        )
        db.add(device)
        db.commit()
        db.refresh(device)
        assert device.status == "在库待售"

        response = client.post(
            "/api/v1/transactions",
            json={
                "device_id": device.id,
                "trade_type": "转售",
                "actual_amount": 3900.0,
                "counterparty_name": "王女士",
                "trade_date": date.today().isoformat(),
                "settlement_method": "现金",
            },
        )
        assert response.status_code == 201, f"{response.status_code}: {response.text}"

        dev_resp = client.get(f"/api/v1/devices/{device.id}")
        assert dev_resp.status_code == 200
        assert dev_resp.json()["status"] == "已售出"
        print("[PASS] test_resale_auto_status - 转售自动更新状态通过")
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("运行后端 API 测试")
    print("=" * 60)
    setup_module()

    test_benchmark_empty_sample()
    test_benchmark_single_transaction()
    test_benchmark_cross_appearance_filter()
    test_transaction_crud()
    test_resale_auto_status()

    print()
    print("=" * 60)
    print("全部测试通过！ ✅")
    print("=" * 60)
