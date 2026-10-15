# 回傳假的推薦商品跟推薦理由
def recommend(cart_items):
    """依購物車回傳推薦品項與理由"""
    print("系統：正在計算推薦商品...")
    return [
        {
            "id": "S01", 
            "name": "起司蛋糕", 
            "price": 80,
            "reason": "買咖啡的人通常也會帶一塊蛋糕喔！"
        }
    ]