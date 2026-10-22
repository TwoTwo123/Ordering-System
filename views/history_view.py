# views/history_view.py
import flet as ft
from components.layout import get_appbar
from services.order_service import list_orders
from services.cart_service import reorder


def history_view(page: ft.Page):
    orders = list_orders()
    order_cards = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)

    def reorder_and_go(order):
        """再點一次：把這筆訂單的餐點加回購物車，回到菜單頁"""
        added, skipped = reorder(order)
        page.go("/")
        if added:
            msg = f"已將 {added} 份餐點加回購物車！"
            if skipped:
                msg += f"（{'、'.join(skipped)} 已下架，未加入）"
            page.snack_bar = ft.SnackBar(ft.Text(msg), duration=2500)
        else:
            page.snack_bar = ft.SnackBar(ft.Text("這筆訂單的餐點都已下架，無法再點一次"), bgcolor="red")
        page.snack_bar.open = True
        page.update()

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
                        # 再點一次：按鈕自己處理點擊，不會觸發整張卡片的「查看收據」
                        ft.OutlinedButton(
                            "再點一次",
                            icon=ft.Icons.REPLAY,
                            style=ft.ButtonStyle(
                                color="#D35400",
                                side=ft.BorderSide(1, "#D35400"),
                                shape=ft.RoundedRectangleBorder(radius=20),
                            ),
                            on_click=lambda e, o=order: reorder_and_go(o),
                        ),
                        ft.Icon(ft.Icons.CHEVRON_RIGHT, color="#222222", size=20)
                    ], spacing=10)
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
