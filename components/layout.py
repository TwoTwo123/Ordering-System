# 這個檔案用來產出畫面上方的「標題列」和最下方的「導覽列」
import flet as ft

def get_appbar(title_text: str):
    """回傳每個頁面上方的標題列"""
    return ft.AppBar(
        title=ft.Text(title_text),
        center_title=True,
<<<<<<< HEAD
        bgcolor=ft.colors.SURFACE_VARIANT, # 用一點淺灰色或主題色襯底區分
=======
        # bgcolor=ft.colors.SURFACE_VARIANT, # 用一點淺灰色或主題色襯底區分
        bgcolor=ft.Colors.ON_SURFACE_VARIANT
>>>>>>> b30500a (完成推薦功能並修復歷史訂單頁面)
    )

def get_navbar(page: ft.Page, current_index: int = 0):
    """
    回傳底部的導覽列。
    current_index 控制目前哪一個按鈕要亮起 (0=菜單, 1=購物車, 2=歷史)
    """
    
    def on_nav_change(e):
        # 當使用者點擊導覽列按鈕時，根據選中的順序決定要切換到哪個路由
        selected = e.control.selected_index
        if selected == 0:
            page.go("/")          # 切換到菜單頁
        elif selected == 1:
            page.go("/cart")      # 切換到購物車頁
        elif selected == 2:
            page.go("/history")   # 切換到歷史紀錄頁

    return ft.NavigationBar(
        selected_index=current_index,
        on_change=on_nav_change,
        destinations=[
            # 可以換圖示
<<<<<<< HEAD
            ft.NavigationDestination(icon=ft.icons.RESTAURANT_MENU, label="菜單"),
            ft.NavigationDestination(icon=ft.icons.SHOPPING_CART, label="購物車"),
            ft.NavigationDestination(icon=ft.icons.RECEIPT_LONG, label="歷史"),
=======
            ft.NavigationBarDestination(icon=ft.Icons.RESTAURANT_MENU, label="菜單"),
            ft.NavigationBarDestination(icon=ft.Icons.SHOPPING_CART, label="購物車"),
            ft.NavigationBarDestination(icon=ft.Icons.RECEIPT_LONG, label="歷史"),
>>>>>>> b30500a (完成推薦功能並修復歷史訂單頁面)
        ]
    )