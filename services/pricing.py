# services/pricing.py

def calc_price(cart_items):
    """計算小計、折扣、總額"""
    subtotal = 0
    for entry in cart_items:
        item = entry.get("item", entry)
        qty = entry.get("qty", 1)
        price = item.get("price", 0) if isinstance(item, dict) else getattr(item, "price", 0)
        subtotal += price * qty
    
    # 滿 300 折 30 折扣邏輯
    discount = 30 if subtotal >= 300 else 0
    total = max(0, subtotal - discount)
    
    return {
        "subtotal": subtotal,
        "discount": discount,
        "total": total
    }