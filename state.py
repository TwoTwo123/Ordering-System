class AppState:
    def __init__(self):
        # 購物車清單：預設為空串列，未來可以存放字典型態的商品資料
        self.cart = []
        
        # 目前使用者：預設為訪客，未來可替換成登入的使用者名稱或 ID
        self.current_user = "Guest"

# 建立全域唯一的狀態物件
# 其他檔案統一 import 這個 app_state 來使用 
app_state = AppState()