# views/receipt_view.py
import flet as ft
import random
import datetime
from services.cart_service import get_cart, clear_cart
from services.pricing import calc_price
from components.cart_sidebar import order_details

# 嘗試安全載入組員 B 的 save_order 函式 (若 B 還沒寫好則使用相容空殼)
try:
    from services.order_service import save_order
except ImportError:
    def save_order(order_data):
        print("【系統日誌】訂單已暫存 (尚未寫入 data/orders.json):", order_data)

def receipt_view(page: ft.Page):
    """結帳收據頁面 (組員 C 結帳核心)"""
    
    cart_items = get_cart()
    pricing = calc_price(cart_items)
    
    order_id = f"ORD-{datetime.datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
    
    # 讀取剛剛在 Modal 輸入的資訊
    dining_val = order_details.get("dining_type", "外送")
    if isinstance(dining_val, (set, list)):
        dining_val = list(dining_val)[0] if dining_val else "外送"

    payment_val = order_details.get("payment_method", "LINE Pay")
    address_val = order_details.get("address", "")
    table_val = order_details.get("table_no", "")
    phone_val = order_details.get("phone", "")
    note_val = order_details.get("note", "")

    # 打包完整訂單物件 (符合組員 B data/orders.json 的格式規格)
    full_order_object = {
        "order_id": order_id,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dining_type": dining_val,
        "payment_method": payment_val,
        "address": address_val,
        "table_no": table_val,
        "phone": phone_val,
        "note": note_val,
        "items": cart_items,
        "subtotal": pricing["subtotal"],
        "discount": pricing["discount"],
        "total": pricing["total"]
    }

    # 正式呼叫組員 B 的 save_order 進行存檔
    save_order(full_order_object)

    # 建立商品明細清單 (深色字體)
    items_detail = ft.Column(spacing=8)
    for entry in cart_items:
        item = entry.get("item", entry)
        qty = entry.get("qty", 1)
        name = item.get("name") if isinstance(item, dict) else item.name
        price = item.get("price", 0) if isinstance(item, dict) else item.price
        
        items_detail.controls.append(
            ft.Row([
                ft.Text(f"{name} x{qty}", size=14, color="#222222", expand=True),
                ft.Text(f"NT${price * qty}", size=14, weight="bold", color="#222222")
            ])
        )

    # 呈現對應的地址 / 桌號 / 備註
    extra_info_rows = []
    if dining_val == "外送" and address_val:
        extra_info_rows.append(ft.Row([ft.Text("外送地址：", weight="bold", color="#333333"), ft.Text(address_val, color="#333333")]))
    elif dining_val == "內用" and table_val:
        extra_info_rows.append(ft.Row([ft.Text("用餐桌號：", weight="bold", color="#333333"), ft.Text(table_val, color="#D35400", weight="bold")]))
    
    if phone_val:
        extra_info_rows.append(ft.Row([ft.Text("聯絡電話：", weight="bold", color="#333333"), ft.Text(phone_val, color="#555555")]))
    if note_val:
        extra_info_rows.append(ft.Row([ft.Text("餐點備註：", weight="bold", color="#333333"), ft.Text(note_val, color="#555555")]))

    def finish_order(e):
        clear_cart() # 結帳完清空購物車
        page.go("/") # 返回主頁

    return ft.View(
        "/receipt",
        controls=[
            ft.AppBar(
                title=ft.Text("訂單結帳收據", size=20, weight="bold", color="white"),
                bgcolor="#D35400",
                leading=ft.IconButton("arrow_back", icon_color="white", on_click=lambda e: page.go("/"))
            ),
            ft.Container(
                content=ft.Column([
                    ft.Icon("check_circle", size=60, color="green500"),
                    ft.Text("訂單已順利送出！", size=22, weight="bold", color="#222222"),
                    ft.Text(f"訂單編號：{order_id}", size=14, color="#666666"),
                    ft.Divider(height=20, color="#E0E0E0"),
                    
                    ft.Container(
                        content=ft.Column([
                            ft.Row([ft.Text("取餐方式：", weight="bold", color="#333333"), ft.Text(str(dining_val), color="#D35400", weight="bold")]),
                            ft.Row([ft.Text("付款方式：", weight="bold", color="#333333"), ft.Text(str(payment_val), color="#555555")]),
                            *extra_info_rows,
                            ft.Row([ft.Text("下單時間：", weight="bold", color="#333333"), ft.Text(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), color="#555555")]),
                        ], spacing=6),
                        bgcolor="#FEF5ED",
                        padding=15,
                        border_radius=8,
                        width=400
                    ),
                    
                    ft.Divider(height=20, color="#E0E0E0"),
                    ft.Text("訂單明細", size=16, weight="bold", color="#222222"),
                    ft.Container(content=items_detail, width=400),
                    ft.Divider(height=20, color="#E0E0E0"),
                    
                    ft.Container(
                        content=ft.Column([
                            ft.Row([ft.Text("小計：", size=14, color="#333333"), ft.Text(f"NT${pricing['subtotal']}", size=14, color="#333333")], alignment="spaceBetween"),
                            ft.Row([ft.Text("滿額優惠折扣：", size=14, color="green700", weight="bold"), ft.Text(f"-NT${pricing['discount']}", size=14, color="green700", weight="bold")], alignment="spaceBetween"),
                            ft.Row([ft.Text("實付總金額：", size=16, weight="bold", color="#222222"), ft.Text(f"NT${pricing['total']}", size=22, weight="bold", color="#D35400")], alignment="spaceBetween"),
                        ], spacing=8),
                        width=400
                    ),
                    
                    ft.Container(height=15),
                    ft.ElevatedButton(
                        "返回菜單 / 繼續點餐",
                        style=ft.ButtonStyle(bgcolor="#D35400", color="white", shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=finish_order,
                        height=45,
                        width=320
                    )
                ], horizontal_alignment="center", spacing=10),
                padding=20,
                alignment=ft.alignment.center
            )
        ]
    )