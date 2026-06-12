from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import date, datetime
from .validators import is_mainstream_brand, validate_imei, normalize_imei


MAINSTREAM_BRANDS = {"苹果", "华为", "小米", "OPPO", "vivo", "三星", "荣耀", "一加", "realme", "魅族"}
APPEARANCE_GRADES = {"全新", "99新", "95新", "9成新", "8成新", "7成新及以下"}
FUNCTION_ITEMS_LIST = [
    "屏幕显示", "触摸功能", "通话功能", "摄像头", "扬声器",
    "麦克风", "振动马达", "指纹识别", "面容识别", "充电接口",
    "耳机接口", "WIFI", "蓝牙", "GPS", "按键"
]
TRADE_TYPES = {"回收", "转售"}
SETTLEMENT_METHODS = {"现金", "转账", "以旧换新抵扣"}
DEVICE_STATUSES = {"在库待售", "已售出", "已回收"}


class InspectionBase(BaseModel):
    inspection_date: date
    appearance_grade: str = Field(..., min_length=1, max_length=10)
    function_items: str
    battery_health: Optional[int] = Field(None, ge=0, le=100)
    estimated_value: Optional[float] = Field(None, ge=0)
    appraiser_signature: str = Field(..., min_length=1, max_length=100)
    notes: Optional[str] = None

    @field_validator("appearance_grade")
    @classmethod
    def validate_appearance_grade(cls, v: str) -> str:
        if v not in APPEARANCE_GRADES:
            raise ValueError(f"外观等级必须是以下之一: {', '.join(APPEARANCE_GRADES)}")
        return v


class InspectionCreate(InspectionBase):
    device_id: int


class InspectionUpdate(BaseModel):
    inspection_date: Optional[date] = None
    appearance_grade: Optional[str] = None
    function_items: Optional[str] = None
    battery_health: Optional[int] = Field(None, ge=0, le=100)
    estimated_value: Optional[float] = Field(None, ge=0)
    appraiser_signature: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("appearance_grade")
    @classmethod
    def validate_appearance_grade(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in APPEARANCE_GRADES:
            raise ValueError(f"外观等级必须是以下之一: {', '.join(APPEARANCE_GRADES)}")
        return v


class Inspection(InspectionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    is_deleted: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class TransactionBase(BaseModel):
    trade_type: str = Field(..., min_length=1, max_length=20)
    actual_amount: float = Field(..., ge=0)
    counterparty_name: str = Field(..., min_length=1, max_length=100)
    trade_date: date
    settlement_method: str = Field(..., min_length=1, max_length=20)
    notes: Optional[str] = None

    @field_validator("trade_type")
    @classmethod
    def validate_trade_type(cls, v: str) -> str:
        if v not in TRADE_TYPES:
            raise ValueError(f"交易类型必须是以下之一: {', '.join(TRADE_TYPES)}")
        return v

    @field_validator("settlement_method")
    @classmethod
    def validate_settlement_method(cls, v: str) -> str:
        if v not in SETTLEMENT_METHODS:
            raise ValueError(f"结算方式必须是以下之一: {', '.join(SETTLEMENT_METHODS)}")
        return v


class TransactionCreate(TransactionBase):
    device_id: int


class TransactionUpdate(BaseModel):
    trade_type: Optional[str] = None
    actual_amount: Optional[float] = Field(None, ge=0)
    counterparty_name: Optional[str] = None
    trade_date: Optional[date] = None
    settlement_method: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("trade_type")
    @classmethod
    def validate_trade_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in TRADE_TYPES:
            raise ValueError(f"交易类型必须是以下之一: {', '.join(TRADE_TYPES)}")
        return v

    @field_validator("settlement_method")
    @classmethod
    def validate_settlement_method(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in SETTLEMENT_METHODS:
            raise ValueError(f"结算方式必须是以下之一: {', '.join(SETTLEMENT_METHODS)}")
        return v


class Transaction(TransactionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    is_deleted: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class BenchmarkResponse(BaseModel):
    brand: str
    model: str
    appearance: Optional[str] = None
    days: int
    count: int
    max_price: Optional[float] = None
    min_price: Optional[float] = None
    avg_price: Optional[float] = None
    median_price: Optional[float] = None


class DeviceBase(BaseModel):
    brand: str = Field(..., min_length=1, max_length=50)
    model: str = Field(..., min_length=1, max_length=100)
    imei: Optional[str] = Field(None, max_length=15)
    storage: Optional[str] = Field(None, max_length=20)
    color: Optional[str] = Field(None, max_length=30)
    purchase_date: Optional[date] = None
    battery_health: Optional[int] = Field(None, ge=0, le=100)
    appearance: Optional[str] = Field(None, max_length=20)
    repair_history: Optional[str] = None
    notes: Optional[str] = None
    estimated_price: Optional[float] = Field(None, ge=0)
    status: Optional[str] = Field("在库待售", max_length=20)


class DeviceCreate(DeviceBase):
    @field_validator("imei")
    @classmethod
    def validate_and_normalize_imei(cls, v: Optional[str], info) -> Optional[str]:
        values = info.data
        brand = values.get("brand")
        if brand and is_mainstream_brand(brand):
            if not v:
                raise ValueError(f"{brand} 为主流品牌，IMEI 为必填项")
            if not validate_imei(v):
                raise ValueError("IMEI 格式无效，请输入正确的15位IMEI号码")
        if v:
            return normalize_imei(v)
        return v

    @field_validator("appearance")
    @classmethod
    def validate_appearance(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in APPEARANCE_GRADES:
            raise ValueError(f"成色必须是以下之一: {', '.join(APPEARANCE_GRADES)}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in DEVICE_STATUSES:
            raise ValueError(f"状态必须是以下之一: {', '.join(DEVICE_STATUSES)}")
        return v


class DeviceUpdate(BaseModel):
    brand: Optional[str] = Field(None, min_length=1, max_length=50)
    model: Optional[str] = Field(None, min_length=1, max_length=100)
    imei: Optional[str] = Field(None, max_length=15)
    storage: Optional[str] = Field(None, max_length=20)
    color: Optional[str] = Field(None, max_length=30)
    purchase_date: Optional[date] = None
    battery_health: Optional[int] = Field(None, ge=0, le=100)
    appearance: Optional[str] = Field(None, max_length=20)
    repair_history: Optional[str] = None
    notes: Optional[str] = None
    estimated_price: Optional[float] = Field(None, ge=0)
    status: Optional[str] = Field(None, max_length=20)

    @field_validator("appearance")
    @classmethod
    def validate_appearance(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in APPEARANCE_GRADES:
            raise ValueError(f"成色必须是以下之一: {', '.join(APPEARANCE_GRADES)}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in DEVICE_STATUSES:
            raise ValueError(f"状态必须是以下之一: {', '.join(DEVICE_STATUSES)}")
        return v


class Device(DeviceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_deleted: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    inspections: List[Inspection] = []
    transactions: List[Transaction] = []


class DeviceListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    brand: str
    model: str
    imei: Optional[str] = None
    storage: Optional[str] = None
    color: Optional[str] = None
    battery_health: Optional[int] = None
    appearance: Optional[str] = None
    estimated_price: Optional[float] = None
    status: Optional[str] = "在库待售"
    created_at: datetime
    inspection_count: int = 0
    transaction_count: int = 0


class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    pages: int
    items: List[DeviceListItem]


class FunctionItemOption(BaseModel):
    key: str
    label: str


class MetadataResponse(BaseModel):
    mainstream_brands: List[str]
    appearance_grades: List[str]
    function_items: List[FunctionItemOption]
    trade_types: List[str]
    settlement_methods: List[str]
    device_statuses: List[str]
