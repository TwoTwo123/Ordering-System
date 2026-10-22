# services/cart_service.py
#
# 購物車資料結構：[ {"item": item_dict, "qty": int, "note": str, "key": str}, ... ]
# - note：單品備註（例如「不要梅粉」），沒有備註時為空字串
# - key ：辨識購物車中「這一行」的代號。同一品項、不同備註會分成不同行
#         沒有備註時 key 就是品項編號（例如 "A01"），所以舊的寫法傳 item_id 仍然可用
#         有備註時 key 為 "品項編號|備註"（例如 "A01|不要梅粉"）

cart_items = []


def _item_id(item):
    return item.get("id") if isinstance(item, dict) else item.id


def make_key(item_id, note=""):
    """產生購物車行的 key"""
    return f"{item_id}|{note}" if note else item_id


def _entry_key(entry):
    return entry.get("key") or _item_id(entry["item"])


def add_item(item, note=""):
    """加入商品；同品項且同備註時數量 +1，否則新增一行"""
    note = (note or "").strip()
    key = make_key(_item_id(item), note)
    for entry in cart_items:
        if _entry_key(entry) == key:
            entry["qty"] += 1
            return cart_items
    cart_items.append({"item": item, "qty": 1, "note": note, "key": key})
    return cart_items


def update_qty(key, qty):
    """修改某一行的數量；數量 <= 0 時移除該行。key 可傳品項編號（無備註的行）"""
    for entry in cart_items:
        if _entry_key(entry) == key:
            entry["qty"] = qty
            break
    cart_items[:] = [e for e in cart_items if e["qty"] > 0]
    return cart_items


def remove_item(key):
    """刪除某一行。key 可傳品項編號（無備註的行）"""
    cart_items[:] = [e for e in cart_items if _entry_key(e) != key]
    return cart_items


def get_cart():
    """取得目前購物車內容"""
    return cart_items


def clear_cart():
    """清空購物車"""
    cart_items.clear()
    return cart_items

def reorder(order):
    """
    再點一次：把一筆舊訂單的餐點加回購物車（保留數量與單品備註）
    價格以「現在的菜單」為準；已下架的品項會略過
    回傳 (加入的份數, 略過的品名清單)
    """
    from services.menu_service import get_item  # 放在函式內，避免循環匯入

    added, skipped = 0, []
    for entry in order.get("items", []):
        old_item = entry.get("item", {})
        item_id = old_item.get("id") if isinstance(old_item, dict) else None
        current = get_item(item_id) if item_id else None
        if not current:
            skipped.append(old_item.get("name", "未知品項") if isinstance(old_item, dict) else "未知品項")
            continue
        for _ in range(entry.get("qty", 1)):
            add_item(current, entry.get("note", ""))
            added += 1
    return added, skipped
