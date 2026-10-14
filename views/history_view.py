# 歷史訂單頁
import flet as ft
from components.layout import get_appbar, get_navbar

def history_view(page: ft.Page):
    return ft.View(
        route="/history",
        appbar=get_appbar("歷史紀錄"),
        controls=[
            ft.Text("這裡是訂單歷史頁", size=24),
            # 在這裡讀取 orders.json 並顯示過去的訂單
        ],
        navigation_bar=get_navbar(page, current_index=2)
    )