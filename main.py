import flet as ft
from components.theme import app_theme
from views.menu_view import menu_view
from views.receipt_view import receipt_view
from views.history_view import history_view

def main(page: ft.Page):
    page.title = "點餐系統"
    page.theme = app_theme
    
    # 關閉預設轉場動畫以消除切換時的閃爍跳動感
    page.theme.page_transitions.windows = ft.PageTransitionTheme.NONE
    page.theme.page_transitions.mac_os = ft.PageTransitionTheme.NONE

    def route_change(e: ft.RouteChangeEvent):
        page.views.clear()
        
        if page.route == "/":
            page.views.append(menu_view(page))
        elif page.route == "/history":
            page.views.append(history_view(page))
        elif page.route.startswith("/receipt"):
            page.views.append(receipt_view(page))
        else:
            page.views.append(menu_view(page))
            
        page.update()

    def view_pop(e: ft.ViewPopEvent):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    route_change(None)

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets", port=39175, view=ft.AppView.WEB_BROWSER)