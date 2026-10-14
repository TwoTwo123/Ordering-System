# 菜單與搜尋頁
import flet as ft
from components.layout import get_appbar, get_navbar

def menu_view(page: ft.Page):
    return ft.View(
        route="/",
        appbar=get_appbar("菜單與搜尋"),
        controls=[
            ft.Text("這裡是菜單頁", size=24),
            # 在這裡新增商品列表與搜尋框
        ],
        navigation_bar=get_navbar(page, current_index=0)
    )