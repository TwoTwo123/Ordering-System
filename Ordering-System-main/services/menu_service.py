# 假菜單
def get_menu():
    """回傳假菜單清單"""
    return [
        {"id": "M01", "name": "招牌拿鐵", "price": 65},
        {"id": "M02", "name": "美式黑咖啡", "price": 50},
        {"id": "M03", "name": "經典紅茶", "price": 30}
    ]

def search_menu(keyword):
    """根據關鍵字搜尋假菜單"""
    print(f"系統：正在搜尋菜單關鍵字 '{keyword}'")
    # 假裝只找到一筆
    return [
        {"id": "M01", "name": "招牌拿鐵", "price": 65}
    ]