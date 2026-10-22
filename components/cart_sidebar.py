# components/cart_sidebar.py
import threading
import flet as ft
from services.cart_service import get_cart, update_qty, remove_item
from services.pricing import calc_price
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

# 調味選項
SPICE_LEVELS = ["不辣", "小辣", "中辣", "大辣"]
TOPPINGS = ["蒜頭", "九層塔", "蔥"]

# 全域訂單詳細資訊
order_details = {
    "dining_type": "外送",
    "payment_method": "LINE Pay",
    "address": "",
    "table_no": "",
    "phone": "",
    "note": "",
    "carrier": "",
    "seasoning": {
        "spice": "不辣",
        "toppings": [],
        "other": "",
    }
}

def build_note_text(spice, toppings, other):
    """把勾選結果組成一行備註文字"""
    parts = [spice] + [f"加{t}" for t in toppings]
    text = " ".join(parts)
    if other:
        text += f"；其他:{other}"
    return text

def _thumb(item):
    """購物車縮圖"""
    photo = item.get("photo") if isinstance(item, dict) else None
    if photo and (ASSETS_DIR / photo).exists():
        return ft.Container(
            content=ft.Image(src=photo, width=40, height=40, fit=ft.ImageFit.COVER),
            width=40, height=40, border_radius=6, clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        )
    img = item.get("img", "") if isinstance(item, dict) else getattr(item, "img", "🍱")
    return ft.Container(
        content=ft.Text(img, size=24),
        width=40, height=40, bgcolor="#FEF5ED", border_radius=6,
        alignment=ft.alignment.center,
    )

def create_cart_sidebar(page: ft.Page, on_change=None, on_cart_change_callback=None):
    cb = on_change or on_cart_change_callback

    cart_items_column = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    pricing_text = ft.Text(size=13, color="#555555")
    discount_hint_text = ft.Text(size=12, color="#D35400", weight="bold")
    total_price_text = ft.Text("NT$0", size=20, weight="bold", color="#D35400")

# --- 階段 3：填寫付款方式、地址/桌號 Modal (拉開間距 + 滿版對齊) ---
    def open_payment_dialog():
        dtype = order_details["dining_type"]

        # 付款方式下拉選單 (不設過短固定寬度，讓它自動 100% 滿版填滿容器)
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
            border_color="#D35400",
            on_change=lambda e: order_details.update({"payment_method": e.control.value})
        )

        address_input = ft.TextField(
            label="外送地址",
            hint_text="請輸入完整地址",
            value=order_details.get("address", ""),
            border_color="#D35400",
            color="#222222"
        )
        table_input = ft.TextField(
            label="桌號",
            hint_text="例如: A05",
            value=order_details.get("table_no", ""),
            border_color="#D35400",
            color="#222222"
        )
        phone_input = ft.TextField(
            label="聯絡電話",
            hint_text="0912-345-678",
            value=order_details.get("phone", ""),
            border_color="#D35400",
            color="#222222"
        )
        carrier_input = ft.TextField(
            label="手機載具 / 統一編號 (選填)",
            hint_text="例: /ABC1234 或 88888888",
            value=order_details.get("carrier", ""),
            border_color="#D35400",
            color="#222222"
        )

        fields = [payment_dropdown]
        if dtype == "外送":
            fields.extend([address_input, phone_input, carrier_input])
        elif dtype == "內用":
            fields.extend([table_input, carrier_input])
        else:
            fields.extend([phone_input, carrier_input])

        def confirm_and_submit_order(e):
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
            order_details["carrier"] = carrier_input.value if carrier_input.value else ""

            page.close(payment_dialog)
            page.go("/receipt")

        payment_dialog = ft.AlertDialog(
            title=ft.Text("填寫訂購資料", size=18, weight="bold", color="#222222"), # 簡化標題，移除多餘的「付款方式」等字樣
            content=ft.Container(
                content=ft.Column(fields, tight=True, spacing=16, scroll=ft.ScrollMode.AUTO), # 間距加大至 16
                width=380, # 拉寬彈窗寬度
                padding=ft.padding.symmetric(vertical=10, horizontal=5) # 內部四周留白，不緊貼邊界
            ),
            actions=[
                ft.TextButton("上一步", on_click=lambda e: page.close(payment_dialog) or open_seasoning_dialog()),
                ft.ElevatedButton(
                    "送出訂單",
                    style=ft.ButtonStyle(bgcolor="#D35400", color="white"),
                    on_click=confirm_and_submit_order
                )
            ]
        )
        page.open(payment_dialog)

    # --- 階段 2：選擇調味 Modal (已修復移除 visual_density 屬性) ---
    def open_seasoning_dialog(e=None):
        cart = get_cart()
        if not cart:
            page.snack_bar = ft.SnackBar(ft.Text("購物車是空的，無法選擇調味喔！"), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return

        label_style = ft.TextStyle(color="#222222", size=13)
        prev = order_details.get("seasoning", {})

        spice_group = ft.RadioGroup(
            value=prev.get("spice", SPICE_LEVELS[0]),
            content=ft.Row(
                [ft.Radio(value=s, label=s, label_style=label_style, active_color="#D35400") for s in SPICE_LEVELS],
                spacing=0
            )
        )

        topping_boxes = [
            ft.Checkbox(
                label=f"加{t}",
                value=(t in prev.get("toppings", [])),
                label_style=label_style,
                active_color="#D35400",
                data=t
            )
            for t in TOPPINGS
        ]

        other_input = ft.TextField(
            label="其他備註 (選填)",
            hint_text="例: 多一點胡椒、分開裝",
            value=prev.get("other", ""),
            border_color="#D35400",
            color="#222222",
            max_length=40
        )

        seasoning_section = ft.Container(
            content=ft.Column([
                ft.Text("辣度", size=12, color="#666666"),
                spice_group,
                ft.Text("配料", size=12, color="#666666"),
                ft.Row(topping_boxes, spacing=0),
                other_input,
            ], spacing=6, tight=True),
            bgcolor="#FEF5ED",
            border_radius=8,
            padding=12,
        )

        def save_seasoning_and_next(e_next):
            spice = spice_group.value or SPICE_LEVELS[0]
            toppings = [cb.data for cb in topping_boxes if cb.value]
            other = (other_input.value or "").strip()

            order_details["seasoning"] = {"spice": spice, "toppings": toppings, "other": other}
            order_details["note"] = build_note_text(spice, toppings, other)

            page.close(seasoning_dialog)
            open_payment_dialog()

        seasoning_dialog = ft.AlertDialog(
            title=ft.Text("🌶️ 請選擇整單調味", size=18, weight="bold", color="#222222"),
            content=ft.Container(
                content=ft.Column([seasoning_section], tight=True, spacing=10),
                width=340
            ),
            actions=[
                ft.TextButton("取消", on_click=lambda e: page.close(seasoning_dialog)),
                ft.ElevatedButton(
                    "選擇付款方式",
                    style=ft.ButtonStyle(bgcolor="#D35400", color="white"),
                    on_click=save_seasoning_and_next
                )
            ]
        )
        page.open(seasoning_dialog)

    # --- 外送 / 外帶 / 內用 按鈕 ---
    def select_dining(type_name):
        order_details["dining_type"] = type_name
        refresh()

    def build_dining_btn(type_name):
        is_selected = (order_details["dining_type"] == type_name)
        return ft.Container(
            content=ft.Text(
                type_name,
                size=14,
                weight="bold" if is_selected else "normal",
                color="#222222" if is_selected else "#666666",
                text_align="center"
            ),
            bgcolor="white" if is_selected else "transparent",
            border_radius=8,
            padding=ft.padding.symmetric(vertical=8),
            alignment=ft.alignment.center,
            expand=True,
            on_click=lambda e, t=type_name: select_dining(t),
            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.BLACK12) if is_selected else None
        )

    dining_bar = ft.Container(
        content=ft.Row([
            build_dining_btn("外送"),
            build_dining_btn("外帶"),
            build_dining_btn("內用"),
        ], spacing=4),
        bgcolor="#F3F3F3",
        padding=4,
        border_radius=10,
        width=310
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
                        ft.Text("點選喜歡的餐點開始選購吧", color="grey400", size=12, no_wrap=True),
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
                note = entry.get("note", "")
                line_key = entry.get("key", item_id)

                minus_icon_name = "delete_outline" if qty == 1 else "remove"
                minus_icon_color = "red600" if qty == 1 else "#D35400"

                # 找到 append(ft.Container(...)) 改成這樣：
                cart_items_column.controls.append(
                    ft.Container(
                        content=ft.Row([
                            _thumb(item),
                            ft.Column([
                                ft.Text(item_name, size=14, weight="bold", color="#222222", no_wrap=True),
                                *([ft.Text(f"備註: {note}", size=11, color="#888888", no_wrap=True)] if note else []),
                                ft.Text(f"NT${item_price}", size=12, color="#666666"),
                            ], expand=True, spacing=2),
                            ft.Container(
                                content=ft.Row([
                                    ft.IconButton(
                                        icon=minus_icon_name,
                                        icon_color=minus_icon_color,
                                        icon_size=18,
                                        on_click=lambda e, k=line_key, q=qty: change_qty(k, q - 1)
                                    ),
                                    ft.Text(str(qty), size=14, weight="bold"),
                                    ft.IconButton(
                                        icon="add",
                                        icon_color="#D35400",
                                        icon_size=18,
                                        on_click=lambda e, k=line_key, q=qty: change_qty(k, q + 1)
                                    ),
                                ], spacing=0, alignment="center"),
                                border=ft.border.all(1, "#E0E0E0"),
                                border_radius=20,
                                padding=ft.padding.symmetric(horizontal=2)
                            )
                        ], alignment="spaceBetween"),
                        padding=ft.padding.symmetric(vertical=6),
                        border=ft.border.only(bottom=ft.BorderSide(1, "#F0F0F0")),
                        width=310  # ★ 加上這行！將餐點卡片寬度強制鎖定 310px，數量按鈕就不會再凸出去了！
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

        dining_bar.content = ft.Row([
            build_dining_btn("外送"),
            build_dining_btn("外帶"),
            build_dining_btn("內用"),
        ], spacing=4)

        page.update()

    def change_qty(line_key, new_qty):
        if new_qty <= 0:
            remove_item(line_key)
        else:
            update_qty(line_key, new_qty)
        refresh()
        if cb:
            cb()

    discount_card = ft.Container(
        content=discount_hint_text,
        bgcolor="#FEF5ED",
        padding=ft.padding.symmetric(horizontal=10, vertical=8),
        border_radius=6,
        width=310
    )

    sidebar_container = ft.Container(
        content=ft.Column([
            dining_bar,
            cart_items_column,
            ft.Divider(height=1, color="#E0E0E0"),
            discount_card,
            ft.Container(
                content=ft.Row([
                    ft.Text("總計:", size=16, weight="bold", color="#222222"),
                    total_price_text
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                width=310
            ),
            ft.ElevatedButton(
                "選擇調味",
                style=ft.ButtonStyle(
                    bgcolor="#D35400",
                    color="white",
                    shape=ft.RoundedRectangleBorder(radius=8)
                ),
                on_click=lambda e: open_seasoning_dialog(e),
                height=45,
                width=310
            )
        ], spacing=12),
        width=340,
        padding=15,
        bgcolor="white",
        border=ft.border.only(left=ft.BorderSide(1, "#E0E0E0")),
        expand=3
    )

    refresh()
    return sidebar_container, refresh