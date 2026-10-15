# components/cart_sidebar.py
import flet as ft
from services.cart_service import get_cart, update_qty, remove_item
from services.pricing import calc_price

# 全域訂單詳細資訊 (供 views/receipt_view.py 讀取)
order_details = {
    "dining_type": "外送",
    "payment_method": "LINE Pay",
    "address": "",
    "table_no": "",
    "phone": "",
    "note": ""
}

def create_cart_sidebar(page: ft.Page):
    """Foodpanda 款式右側購物車 (包含訂單資料收集 Modal)"""
    
    cart_items_column = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    pricing_text = ft.Text(size=13, color="#555555")
    discount_hint_text = ft.Text(size=12, color="#D35400", weight="bold")
    total_price_text = ft.Text("NT$0", size=20, weight="bold", color="#D35400")

    def on_dining_change(e):
        val = list(e.data)[0] if isinstance(e.data, (set, list)) else e.data
        order_details["dining_type"] = val if val else "外送"
        refresh()

    dining_segmented = ft.SegmentedButton(
        segments=[
            ft.Segment(value="外送", label=ft.Text("外送", size=12)),
            ft.Segment(value="外帶自取", label=ft.Text("外帶", size=12)),
            ft.Segment(value="內用", label=ft.Text("內用", size=12)),
        ],
        selected={order_details["dining_type"]},
        on_change=on_dining_change
    )

    payment_dropdown = ft.Dropdown(
        value=order_details["payment_method"],
        options=[
            ft.dropdown.Option("LINE Pay"),
            ft.dropdown.Option("信用卡 / 簽帳卡"),
            ft.dropdown.Option("現場現金付款"),
        ],
        label="付款方式",
        dense=True,
        text_size=13,
        on_change=lambda e: order_details.update({"payment_method": e.control.value})
    )

    def refresh():
        cart = get_cart()
        pricing = calc_price(cart)
        subtotal = pricing["subtotal"]
        
        cart_items_column.controls.clear()
        
        if not cart:
            cart_items_column.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon("shopping_bag_outlined", size=48, color="grey400"),
                        ft.Text("購物車是空的喔！", color="#777777", size=14, weight="bold"),
                        ft.Text("點選喜歡的餐點開始選購吧", color="grey400", size=12),
                    ], alignment="center", horizontal_alignment="center"),
                    padding=20,
                    alignment=ft.alignment.center
                )
            )
            total_price_text.value = "NT$0"
            pricing_text.value = "小計: NT$0 | 折扣: -NT$0"
            discount_hint_text.value = "💡 滿 NT$300 即享 NT$30 折扣！"
        else:
            for entry in cart:
                item = entry.get("item", entry)
                qty = entry.get("qty", 1)
                item_id = item.get("id") if isinstance(item, dict) else item.id
                item_name = item.get("name") if isinstance(item, dict) else item.name
                item_price = item.get("price", 0) if isinstance(item, dict) else item.price
                item_img = item.get("img", "🍗") if isinstance(item, dict) else getattr(item, "img", "🍗")

                minus_icon_name = "delete_outline" if qty == 1 else "remove"
                minus_icon_color = "red600" if qty == 1 else "#D35400"

                cart_items_column.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Text(item_img, size=24),
                                width=40, height=40, bgcolor="#FEF5ED", border_radius=6, alignment=ft.alignment.center
                            ),
                            ft.Column([
                                ft.Text(item_name, size=14, weight="bold", color="#222222", no_wrap=True),
                                ft.Text(f"NT${item_price}", size=12, color="#666666"),
                            ], expand=True, spacing=2),
                            ft.Container(
                                content=ft.Row([
                                    ft.IconButton(
                                        icon=minus_icon_name,
                                        icon_color=minus_icon_color,
                                        icon_size=18,
                                        on_click=lambda e, i_id=item_id, q=qty: change_qty(i_id, q - 1)
                                    ),
                                    ft.Text(str(qty), size=14, weight="bold", color="#222222"),
                                    ft.IconButton(
                                        icon="add",
                                        icon_color="#D35400",
                                        icon_size=18,
                                        on_click=lambda e, i_id=item_id, q=qty: change_qty(i_id, q + 1)
                                    ),
                                ], spacing=0, alignment="center"),
                                border=ft.border.all(1, "#E0E0E0"),
                                border_radius=20,
                                padding=ft.padding.symmetric(horizontal=2)
                            )
                        ], alignment="spaceBetween"),
                        padding=ft.padding.symmetric(vertical=6),
                        border=ft.border.only(bottom=ft.BorderSide(1, "#F0F0F0"))
                    )
                )

            pricing_text.value = f"小計: NT${subtotal} | 折扣: -NT${pricing['discount']}"
            
            if subtotal >= 300:
                discount_hint_text.value = "🎉 已符合滿 $300 折 $30 優惠！"
                discount_hint_text.color = "green700"
            else:
                needed = 300 - subtotal
                discount_hint_text.value = f"💡 再加點 NT${needed} 即可折 NT$30！"
                discount_hint_text.color = "#D35400"

            total_price_text.value = f"NT${pricing['total']}"

        page.update()

    def change_qty(item_id, new_qty):
        if new_qty <= 0:
            remove_item(item_id)
        else:
            update_qty(item_id, new_qty)
        refresh()

    def open_checkout_dialog(e):
        if not get_cart():
            page.snack_bar = ft.SnackBar(ft.Text("購物車是空的，無法結帳喔！"))
            page.snack_bar.open = True
            page.update()
            return

        # 1. 精準解包 SegmentedButton 傳過來的 set 資料，取得純字串 (例如 "內用")
        raw_dtype = order_details["dining_type"]
        if isinstance(raw_dtype, (set, list)):
            dtype = list(raw_dtype)[0] if raw_dtype else "外送"
        else:
            dtype = raw_dtype if raw_dtype else "外送"

        # 2. 加入 color="#222222" 解決字體變白的問題，並加上深色背景對比
        address_input = ft.TextField(
            label="外送地址", 
            hint_text="請輸入完整地址", 
            border_color="#D35400", 
            color="#222222"
        )
        table_input = ft.TextField(
            label="桌號", 
            hint_text="例如: A05", 
            border_color="#D35400", 
            color="#222222"
        )
        phone_input = ft.TextField(
            label="聯絡電話", 
            hint_text="0912-345-678", 
            border_color="#D35400", 
            color="#222222"
        )
        note_input = ft.TextField(
            label="餐點備註", 
            hint_text="例: 加蒜/中辣/不要香菜", 
            border_color="#D35400", 
            color="#222222"
        )

        # 3. 根據純字串精準切換內用、外送與外帶欄位
        fields = []
        if dtype == "外送":
            fields.extend([address_input, phone_input, note_input])
        elif dtype == "內用":
            fields.extend([table_input, note_input])  # 內用只出現桌號與備註！
        else:  # 外帶自取
            fields.extend([phone_input, note_input])

        def confirm_and_pay(e):
            if dtype == "外送" and not address_input.value:
                address_input.error_text = "請輸入外送地址！"
                page.update()
                return
            if dtype == "內用" and not table_input.value:
                table_input.error_text = "請輸入桌號！"
                page.update()
                return

            order_details["address"] = address_input.value if address_input.value else ""
            order_details["table_no"] = table_input.value if table_input.value else ""
            order_details["phone"] = phone_input.value if phone_input.value else ""
            order_details["note"] = note_input.value if note_input.value else ""
            
            page.close(checkout_dialog)
            page.go("/receipt")

        checkout_dialog = ft.AlertDialog(
            title=ft.Text(f"📋 請填寫訂單資訊 ({dtype})", size=18, weight="bold", color="#222222"),
            content=ft.Container(
                content=ft.Column(fields, tight=True, spacing=10),
                width=340
            ),
            actions=[
                ft.TextButton("取消", on_click=lambda e: page.close(checkout_dialog)),
                ft.ElevatedButton(
                    "確認送出訂單",
                    style=ft.ButtonStyle(bgcolor="#D35400", color="white"),
                    on_click=confirm_and_pay
                )
            ]
        )
        page.open(checkout_dialog)

    sidebar_container = ft.Container(
        content=ft.Column([
            ft.Text("🛒 你的購物車", size=18, weight="bold", color="#222222"),
            dining_segmented,
            ft.Divider(height=1, color="#E0E0E0"),
            cart_items_column,
            ft.Divider(height=1, color="#E0E0E0"),
            discount_hint_text,
            payment_dropdown,
            pricing_text,
            ft.Row([
                ft.Text("總計:", size=16, weight="bold", color="#222222"),
                total_price_text
            ], alignment="spaceBetween"),
            ft.ElevatedButton(
                "前往填寫資料並結帳",
                style=ft.ButtonStyle(bgcolor="#D35400", color="white", shape=ft.RoundedRectangleBorder(radius=8)),
                on_click=open_checkout_dialog,
                height=45,
                width=300
            )
        ], spacing=10),
        width=340,
        padding=15,
        bgcolor="white",
        border=ft.border.only(left=ft.BorderSide(1, "#E0E0E0")),
        expand=3
    )

    refresh()
    return sidebar_container, refresh