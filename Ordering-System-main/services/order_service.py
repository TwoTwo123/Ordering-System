# 接收訂單和回傳歷史紀錄的空殼
def save_order(order):
    """送出訂單"""
    print(f"系統：已成功儲存訂單資料 -> {order}")
    return True

def list_orders():
    """查詢歷史訂單"""
    return [
        {"order_id": "ORD-001", "total": 130, "date": "2026-10-14"},
        {"order_id": "ORD-002", "total": 250, "date": "2026-10-13"}
    ]