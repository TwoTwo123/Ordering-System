# services/order_service.py（組員 B）
# 訂單存在 data/orders.json，格式沿用 receipt_view.py 的 full_order_object
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ORDERS_FILE = DATA_DIR / "orders.json"


def _read_all():
    """讀出所有訂單；檔案不存在或內容壞掉時回傳空清單"""
    if not ORDERS_FILE.exists():
        return []
    try:
        with open(ORDERS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def _write_all(orders):
    DATA_DIR.mkdir(exist_ok=True)
    # ensure_ascii=False 讓中文直接寫成中文，打開檔案看得懂
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)


def save_order(order):
    """新增一筆訂單，成功回傳 True"""
    orders = _read_all()
    orders.append(order)
    _write_all(orders)
    return True


def list_orders(limit=None):
    """回傳歷史訂單，最新的在前面；給 limit 時只回傳前幾筆"""
    orders = sorted(_read_all(), key=lambda o: o.get("created_at", ""), reverse=True)
    return orders[:limit] if limit else orders


def get_order(order_id):
    """依訂單編號查詢單筆訂單，找不到回傳 None"""
    for order in _read_all():
        if order.get("order_id") == order_id:
            return order
    return None
