# views/receipt_view.py
import flet as ft
import random
import datetime
from services.cart_service import get_cart, clear_cart
from services.pricing import calc_price
from components.cart_sidebar import order_details
from services.order_service import get_order

try:
    from services.order_service import save_order
except ImportError:
    def save_order(order_data):
        print("【系統日誌】訂單已暫存", order_data)

def receipt_view(page: ft.Page):
    """結帳收據頁面"""
    
    # 判斷是否為歷史訂單查詢 (透過 URL ?id=xxx 帶入)
    query_id = None
    if "?" in page.route:
        parts = page.route.split("?id=")
        if len(parts) > 1:
            query_id = parts[1]

    hist_order = get_order(query_id) if query_id else None

    if hist_order:
        # 讀取歷史訂單資料
        order_id = hist_order.get("order_id")
        dining_val = hist_order.get("dining_type", "外送")
        payment_val = hist_order.get("payment_method", "LINE Pay")
        address_val = hist_order.get("address", "")
        table_val = hist_order.get("table_no", "")
        phone_val = hist_order.get("phone", "")
        note_val = hist_order.get("note", "")
        carrier_val = hist_order.get("carrier", "")
        created_time = hist_order.get("created_at", "")
        cart_items = hist_order.get("items", [])
        pricing = {
            "subtotal": hist_order.get("subtotal", 0),
            "discount": hist_order.get("discount", 0),
            "total": hist_order.get("total", 0)
        }
    else:
        # 讀取當前剛送出的購物車訂單
        cart_items = get_cart()
        pricing = calc_price(cart_items)
        order_id = f"ORD-{datetime.datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        
        dining_val = order_details.get("dining_type", "外送")
        if isinstance(dining_val, (set, list)):
            dining_val = list(dining_val)[0] if dining_val else "外送"
        
        payment_val = order_details.get("payment_method", "LINE Pay")
        address_val = order_details.get("address", "")
        table_val = order_details.get("table_no", "")
        phone_val = order_details.get("phone", "")
        note_val = order_details.get("note", "")
        carrier_val = order_details.get("carrier", "")
        created_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        full_order_object = {
            "order_id": order_id,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "dining_type": dining_val,
            "payment_method": payment_val,
            "address": address_val,
            "table_no": table_val,
            "phone": phone_val,
            "note": note_val,
            "carrier": carrier_val,
            "seasoning": order_details.get("seasoning", {}),
            "items": cart_items,
            "subtotal": pricing["subtotal"],
            "discount": pricing["discount"],
            "total": pricing["total"]
        }
        if cart_items:
            save_order(full_order_object)

    # 取餐方式字串防呆修正（避免出現 ['內用'] 格式）
    if isinstance(dining_val, (list, set)):
        dining_val = list(dining_val)[0] if dining_val else "外送"

    # 商品明細渲染
    items_detail = ft.Column(spacing=8)
    for entry in cart_items:
        item = entry.get("item", entry)
        qty = entry.get("qty", 1)
        name = item.get("name") if isinstance(item, dict) else getattr(item, "name", "餐點")
        price = item.get("price", 0) if isinstance(item, dict) else getattr(item, "price", 0)
        note = entry.get("note", "")

        items_detail.controls.append(
            ft.Row([
                ft.Column([
                    ft.Text(f"{name} x{qty}", size=14, color="#222222"),
                    *([ft.Text(f"備註: {note}", size=12, color="#888888")] if note else []),
                ], spacing=2, expand=True),
                ft.Text(f"NT${price * qty}", size=14, weight="bold", color="#222222")
            ])
        )

    extra_info_rows = []
    if dining_val == "外送" and address_val:
        extra_info_rows.append(ft.Row([ft.Text("外送地址：", weight="bold", color="#333333"), ft.Text(address_val, color="#333333")]))
    elif dining_val == "內用" and table_val:
        extra_info_rows.append(ft.Row([ft.Text("用餐桌號：", weight="bold", color="#333333"), ft.Text(table_val, color="#D35400", weight="bold")]))
    if phone_val:
        extra_info_rows.append(ft.Row([ft.Text("聯絡電話：", weight="bold", color="#333333"), ft.Text(phone_val, color="#555555")]))
    if note_val:
        extra_info_rows.append(ft.Row([ft.Text("調味備註：", weight="bold", color="#333333"), ft.Text(note_val, color="#555555", expand=True)]))
    if carrier_val:
        extra_info_rows.append(ft.Row([ft.Text("載具 / 統編：", weight="bold", color="#333333"), ft.Text(carrier_val, color="#555555")]))

    def finish_order(e):
        clear_cart()
        page.go("/history") # 完成或返回時回到購買紀錄頁面

    # 主要收據可捲動內容區塊
    receipt_content = ft.Column([
        ft.Icon("check_circle", size=60, color="green500"),
        ft.Text("訂單已順利送出！", size=22, weight="bold", color="#222222"),
        ft.Text(f"訂單編號：{order_id}", size=14, color="#666666"),
        ft.Divider(height=20, color="#E0E0E0"),
        ft.Container(
            content=ft.Column([
                ft.Row([ft.Text("取餐方式：", weight="bold", color="#333333"), ft.Text(str(dining_val), color="#D35400", weight="bold")]),
                ft.Row([ft.Text("付款方式：", weight="bold", color="#333333"), ft.Text(str(payment_val), color="#555555")]),
                *extra_info_rows,
                ft.Row([ft.Text("下單時間：", weight="bold", color="#333333"), ft.Text(created_time, color="#555555")]),
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
            ], spacing=6),
            width=400
        ),
        ft.Container(height=15),
        ft.ElevatedButton(
            "返回購買紀錄",
            style=ft.ButtonStyle(bgcolor="#D35400", color="white", shape=ft.RoundedRectangleBorder(radius=8)),
            on_click=finish_order,
            height=45,
            width=320
        ),
        ft.Container(height=20)
    ], horizontal_alignment="center", spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

    return ft.View(
        "/receipt",
        appbar=ft.AppBar(
            title=ft.Text("訂單結帳收據", weight="bold", color="white", size=20),
            bgcolor="#D35400",
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color="white",
                on_click=lambda e: page.go("/history") # 左上角返回鍵：回到購買紀錄頁面
            )
        ),
        controls=[
            ft.Container(
                content=receipt_content,
                padding=20,
                alignment=ft.alignment.center,
                expand=True
            )
        ],
        padding=0,
        spacing=0
    )