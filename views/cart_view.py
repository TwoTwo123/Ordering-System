# 購物車頁
import flet as ft
from components.layout import get_appbar, get_navbar

def cart_view(page: ft.Page):
    return ft.View(
        route="/cart",
        appbar=get_appbar("我的購物車"),
        controls=[
            ft.Text("這裡是購物車頁", size=24),
            # 在這裡顯示購物車清單，並加上「前往結帳」按鈕
        ],
        navigation_bar=get_navbar(page, current_index=1)
    )