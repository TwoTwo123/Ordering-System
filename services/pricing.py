# 計價邏輯實作前先回傳固定格式的字典，這樣結帳頁面可以先排版。
def calc_price(cart_items):
    """計算小計、折扣、總額"""
    print("系統：正在計算購物車總額...")
    return {
        "subtotal": 100,  # 小計
        "discount": 0,    # 折扣
        "total": 100      # 最終總額
    }