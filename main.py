import flet as ft

# 匯入建立的主題設定
from components.theme import app_theme

# 匯入建立的所有空殼頁面
from views.menu_view import menu_view
from views.cart_view import cart_view
from views.receipt_view import receipt_view
from views.history_view import history_view

def main(page: ft.Page):
    # 1. 基本頁面設定
    page.title = "點餐系統"
    page.theme = app_theme  # 套用字級與主色系

    # 2. 路由改變時的處理邏輯
    def route_change(e: ft.RouteChangeEvent):
        # 每次切換路由時，先清空當前的畫面堆疊
        page.views.clear()

        # 根據現在的路徑 (page.route) 把對應的 View 塞進畫面堆疊裡
        if page.route == "/":
            page.views.append(menu_view(page))
        elif page.route == "/cart":
            page.views.append(cart_view(page))
        elif page.route == "/receipt":
            page.views.append(receipt_view(page))
        elif page.route == "/history":
            page.views.append(history_view(page))
        else:
            # 防呆：如果輸入了不存在的路由，預設回到首頁
            page.views.append(menu_view(page))

        # 畫面堆疊更新後，必須呼叫 page.update() 才會重新渲染
        page.update()

    # 3. 處理「返回上一頁」的邏輯（例如在收據頁點擊返回，或按了手機的返回鍵）
    def view_pop(e: ft.ViewPopEvent):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    # 4. 將寫好的邏輯綁定到 page 的事件上
    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # 5. 程式啟動時，觸發前往首頁
    page.go("/")

# 讓 Flet 啟動這個 main 函式
if __name__ == "__main__":
    ft.app(target=main)