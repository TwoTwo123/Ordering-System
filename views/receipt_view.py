# 結帳收據頁
import flet as ft
from components.layout import get_appbar

def receipt_view(page: ft.Page):
    return ft.View(
        route="/receipt",
        appbar=get_appbar("結帳成功"),
        controls=[
            ft.Text("這裡是結帳收據頁", size=24),
            # 在這裡顯示訂單明細與總金額
            ft.ElevatedButton("返回菜單", on_click=lambda e: page.go("/"))
        ],
        # 結帳完成後顯示收據頁面，通常不需要再顯示底部導覽列，使用者看完後點擊按鈕返回
        # 可能需要一個返回首頁的按鈕
    )