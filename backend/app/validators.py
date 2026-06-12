import re
from typing import Optional

MAINSTREAM_BRANDS = {"苹果", "华为", "小米", "OPPO", "vivo", "三星", "荣耀", "一加", "realme", "魅族"}

IMEI_PATTERN = re.compile(r'^\d{15}$')


def is_mainstream_brand(brand: str) -> bool:
    return brand in MAINSTREAM_BRANDS


def validate_imei(imei: str) -> bool:
    if not imei:
        return False
    imei_clean = imei.replace(' ', '').replace('-', '')
    if not IMEI_PATTERN.match(imei_clean):
        return False
    return luhn_check(imei_clean)


def luhn_check(imei: str) -> bool:
    if len(imei) != 15:
        return False
    digits = [int(d) for d in imei[:14]]
    for i in range(len(digits) - 1, -1, -2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    total = sum(digits)
    check_digit = (10 - (total % 10)) % 10
    return check_digit == int(imei[14])


def normalize_imei(imei: Optional[str]) -> Optional[str]:
    if not imei:
        return None
    return imei.replace(' ', '').replace('-', '')


def format_imei(imei: str) -> str:
    imei = normalize_imei(imei) or ''
    if len(imei) == 15:
        return f"{imei[:3]} {imei[3:8]} {imei[8:14]} {imei[14:]}"
    return imei
