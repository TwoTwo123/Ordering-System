# views/history_view.py
import flet as ft
from components.layout import get_appbar
from services.order_service import list_orders

def history_view(page: ft.Page):
    orders = list_orders()
    order_cards = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)
    
    if not orders:
        order_cards.controls.append(
            ft.Container(
                content=ft.Text("目前尚無購買紀錄", color="grey500", size=16),
                padding=40,
                alignment=ft.alignment.center
            )
        )
    else:
        for order in orders:
            order_id = order.get("order_id", "")
            created_at = order.get("created_at", "")
            total = order.get("total", 0)
            
            items_summary = ", ".join([
                f"{entry.get('item', {}).get('name', '餐點')} x{entry.get('qty', 1)}"
                for entry in order.get("items", [])
            ])
            
            card = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.SHOPPING_CART_OUTLINED, size=28, color="#222222"),
                    ft.Column([
                        ft.Row([
                            ft.Text("Order", weight="bold", size=15, color="#222222"),
                            ft.Text(created_at, size=13, color="#888888"),
                        ], spacing=8),
                        ft.Text(items_summary, size=13, color="#666666", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ], expand=True, spacing=2),
                    ft.Row([
                        ft.Text(f"$ {total}", size=16, weight="bold", color="#222222"),
                        ft.Icon(ft.Icons.CHEVRON_RIGHT, color="#222222", size=20)
                    ], spacing=4)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor="#F5F5F5",
                border_radius=8,
                padding=15,
                on_click=lambda e, oid=order_id: page.go(f"/receipt?id={oid}")
            )
            order_cards.controls.append(card)

    return ft.View(
        "/history",
        appbar=get_appbar("購買紀錄", page, show_back=True),
        controls=[
            ft.Container(
                content=order_cards,
                padding=20,
                expand=True
            )
        ],
        padding=0,
        spacing=0
    )