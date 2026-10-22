import os

from ..cipher.crypto import Crypto
from ..cipher.aes import AES
from ..cipher.des import DES
from ..cipher.rc4 import RC4
from ..exceptions import CryptoMethodError
import json

from .decrypt import decrypt_data
from .encrypt import encrypt_data

def _safe_float(value, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def _safe_int(value, default: int = 0) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def decrypt_record(record) -> list[dict]:
    payload = decrypt_data(record.encrypted_payload)

    # 1. Ekstrak data pasien dari payload
    record.name = payload.get("name") or ""
    record.age = _safe_float(payload.get("age"), 0.0)
    record.weight = _safe_float(payload.get("weight"), 0.0)
    record.height = _safe_float(payload.get("height"), 1.0)
    record.glucose = _safe_float(payload.get("glucose"), 0.0)
    record.gender = payload.get("gender") or "Other"
    record.ever_married = payload.get("ever_married") or "No"
    record.work_type = payload.get("work_type") or "Private"
    record.residence = payload.get("residence") or "Urban"
    record.smoking = payload.get("smoking") or "Unknown"
    record.hypertension = _safe_int(payload.get("hypertension"), 0)
    record.heart_disease = _safe_int(payload.get("heart_disease"), 0)

    # hitung bmi
    if record.height > 0:
        record.bmi = record.weight / ((record.height / 100) ** 2)
    else:
        record.bmi = 0.0


    # risk score (ga di encrypt)
    record.prediction = record.risk_score

    return record


def decrypt_records(records):
    return [decrypt_record(r) for r in records]

def decrypt_records(records) -> list[dict]:
    return [decrypt_record(r) for r in records]