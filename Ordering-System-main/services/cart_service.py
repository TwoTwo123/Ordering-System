# services/cart_service.py

# 全域購物車資料結構：[ {"item": item_dict, "qty": int}, ... ]
cart_items = []

def add_item(item):
    """加入商品或增加數量"""
    for cart_item in cart_items:
        # 判斷是否為同一個商品 (支援 dict 與物件兩種格式)
        item_id = item.get("id") if isinstance(item, dict) else item.id
        c_id = cart_item["item"].get("id") if isinstance(cart_item["item"], dict) else cart_item["item"].id
        
        if c_id == item_id:
            cart_item["qty"] += 1
            return cart_items
            
    cart_items.append({"item": item, "qty": 1})
    return cart_items

def update_qty(item_id, qty):
    """修改數量"""
    global cart_items
    for cart_item in cart_items:
        c_id = cart_item["item"].get("id") if isinstance(cart_item["item"], dict) else cart_item["item"].id
        if c_id == item_id:
            cart_item["qty"] = qty
            break
            
    # 數量小於等於 0 時自動從購物車中移除
    cart_items = [i for i in cart_items if i["qty"] > 0]
    return cart_items

def remove_item(item_id):
    """刪除商品"""
    global cart_items
    cart_items = [
        i for i in cart_items 
        if (i["item"].get("id") if isinstance(i["item"], dict) else i["item"].id) != item_id
    ]
    return cart_items

def get_cart():
    """取得目前購物車內容"""
    return cart_items

def clear_cart():
    """清空購物車"""
    global cart_items
    cart_items = []
    return cart_items