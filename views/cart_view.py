# views/cart_view.py
import flet as ft
from services.cart_service import get_cart, update_qty, remove_item
from services.pricing import calc_price
from services.recommender import recommend

def cart_view(page: ft.Page):
    """購物車頁面 View"""
    
    # 重新繪製/更新購物車 UI 的邏輯
    def refresh_cart_ui():
        cart_items = get_cart()
        pricing = calc_price(cart_items)

        items_list.controls.clear()

        if not cart_items:
            items_list.controls.append(
                ft.Container(
                    content=ft.Text("目前購物車是空的喔！", size=16, color="grey500"),
                    padding=20,
                    alignment=ft.alignment.center
                )
            )
        else:
            for entry in cart_items:
                item = entry.get("item", entry)
                qty = entry.get("qty", 1)
                item_id = item.get("id") if isinstance(item, dict) else item.id
                item_name = item.get("name") if isinstance(item, dict) else item.name
                item_price = item.get("price", 0) if isinstance(item, dict) else item.price
                note = entry.get("note", "")
                line_key = entry.get("key", item_id)  # 同品項不同備註是不同行，用 key 區分

                name_block = ft.Column([
                    ft.Text(item_name, size=15, weight="bold"),
                    *([ft.Text(f"備註：{note}", size=12, color="grey600")] if note else []),
                ], spacing=2, expand=True)

                items_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            name_block,
                            ft.IconButton(
                                "remove",
                                on_click=lambda e, k=line_key, q=qty: on_qty_change(k, q - 1)
                            ),
                            ft.Text(str(qty), size=15, weight="bold"),
                            ft.IconButton(
                                "add",
                                on_click=lambda e, k=line_key, q=qty: on_qty_change(k, q + 1)
                            ),
                            ft.Text(f"${item_price * qty}", width=60, text_align="right", color="red700", weight="bold"),
                        ]),
                        padding=5,
                        border=ft.border.only(bottom=ft.BorderSide(1, "grey200"))
                    )
                )

        price_text.value = f"小計: ${pricing['subtotal']} | 折扣: -${pricing['discount']}\n總金額: ${pricing['total']}"
        page.update()

    def on_qty_change(item_id, new_qty):
        if new_qty <= 0:
            remove_item(item_id)
        else:
            update_qty(item_id, new_qty)
        refresh_cart_ui()

    # 畫面控制項定義
    items_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    price_text = ft.Text(size=18, weight="bold", color="green700")

    recommend_card_stub = ft.Container(
        content=ft.Column(recommend(get_cart())),
        bgcolor="amber50",
        border=ft.border.all(1, "amber200"),
        border_radius=8,
        padding=10,
        margin=ft.margin.only(bottom=10)
    )

    # 首次載入畫面數據
    refresh_cart_ui()

    return ft.View(
        "/cart",
        controls=[
            ft.AppBar(
                title=ft.Text("我的購物車"), 
                bgcolor="red400", 
                color="white",
                leading=ft.IconButton("arrow_back", on_click=lambda e: page.go("/"))
            ),
            recommend_card_stub,
            items_list,
            ft.Divider(),
            ft.Container(
                content=ft.Column([
                    price_text,
                    ft.ElevatedButton(
                        "前往結帳",
                        icon="check_circle",
                        style=ft.ButtonStyle(bgcolor="green600", color="white"),
                        on_click=lambda e: page.go("/receipt") if get_cart() else page.show_snack_bar(ft.SnackBar(ft.Text("購物車是空的喔！"))),
                        width=360
                    )
                ]),
                padding=10
            )
        ]
    )