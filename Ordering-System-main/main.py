import flet as ft

# 匯入建立的主題設定與頁面
from components.theme import app_theme
from views.menu_view import menu_view
from views.cart_view import cart_view
from views.receipt_view import receipt_view
from views.history_view import history_view

def main(page: ft.Page):
    # 1. 基本頁面設定
    page.title = "點餐系統"
    page.theme = app_theme  # 套用主題

    # 2. 路由改變時的處理邏輯
    def route_change(e: ft.RouteChangeEvent):
        page.views.clear()
        
        if page.route == "/":
            page.views.append(menu_view(page))
        elif page.route == "/cart":
            page.views.append(cart_view(page))
        elif page.route == "/receipt":
            page.views.append(receipt_view(page))
        elif page.route == "/history":
            page.views.append(history_view(page))
        else:
            page.views.append(menu_view(page))
            
        page.update()

    # 3. 處理「返回上一頁」邏輯
    def view_pop(e: ft.ViewPopEvent):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)

    # 4. 綁定事件
    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # 5. 關鍵修正：直接手動觸發一次路由渲染，避免初始化空白！
    route_change(None)

if __name__ == "__main__":
    ft.app(target=main)