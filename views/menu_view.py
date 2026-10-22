# views/menu_view.py
import flet as ft
from services.cart_service import add_item, update_qty, remove_item, get_cart
from components.cart_sidebar import create_cart_sidebar
from services.menu_service import get_menu, get_categories, search_menu
from pathlib import Path
from services.order_service import get_best_sellers
from components.layout import get_appbar


# 照片放在 assets/images/，menu.json 的 "photo" 欄位寫相對於 assets 的路徑（例如 "images/A01.jpg"）
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def food_visual(item, width, height, emoji_size, border_radius=None):
    """有照片就顯示照片，找不到照片檔就顯示 emoji，照片可以慢慢補齊"""
    photo = item.get("photo")
    if photo and (ASSETS_DIR / photo).exists():
        return ft.Container(
            content=ft.Image(src=photo, width=width, height=height, fit=ft.ImageFit.COVER),
            width=width, height=height, border_radius=border_radius,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        )
    return ft.Container(
        content=ft.Text(item["img"], size=emoji_size),
        alignment=ft.alignment.center, width=width, height=height,
        bgcolor="#FEF5ED", border_radius=border_radius,
    )


def menu_view(page: ft.Page):
    """菜單主頁 View"""
    current_category = "全部"
    search_keyword = ""
    best_sellers = get_best_sellers(3)  # 熱銷前 3 名，依 data/orders.json 統計
    stepper_refreshers = {}  # 品項編號 -> 更新該卡片數量顯示的函式

    def refresh_all_steppers():
        """購物車變動時，更新每張卡片上的數量（不重建整個菜單，避免照片閃爍）"""
        for fn in stepper_refreshers.values():
            fn()
        page.update()

    # 側邊購物車按加減時，也要同步更新卡片上的數量
    cart_sidebar_ui, refresh_cart = create_cart_sidebar(page, on_cart_change_callback=refresh_all_steppers)

    def card_qty(item_id):
        """卡片上的數量 = 購物車中「沒有備註」那一行的數量（有備註的請到購物車調整）"""
        for entry in get_cart():
            if entry.get("key", entry["item"]["id"]) == item_id:
                return entry["qty"]
        return 0

    def set_card_qty(item, qty):
        if qty <= 0:
            remove_item(item["id"])
        elif card_qty(item["id"]) == 0:
            add_item(item)
        else:
            update_qty(item["id"], qty)
        refresh_cart()
        refresh_all_steppers()

    def open_item_modal(item):
        modal_qty = 1
        qty_text = ft.Text(str(modal_qty), size=18, weight="bold", color="#222222")

        def update_modal_qty(delta):
            nonlocal modal_qty
            if modal_qty + delta >= 1:
                modal_qty += delta
                qty_text.value = str(modal_qty)
                modal_submit_btn.text = f"放入購物車 • NT${item['price'] * modal_qty}"
                page.update()

        # 單品備註：同品項不同備註會在購物車分成不同行
        note_field = ft.TextField(
            label="餐點備註（選填）",
            hint_text="例：不要梅粉、切小塊",
            max_length=30,
            text_size=14,
            border_color="#D35400",
            focused_border_color="#D35400",
            color="#222222",
        )

        def add_modal_to_cart(e):
            note = (note_field.value or "").strip()
            for _ in range(modal_qty):
                add_item(item, note)
            refresh_cart()
            refresh_all_steppers()
            page.close(modal_dialog)
            note_msg = f"（{note}）" if note else ""
            page.snack_bar = ft.SnackBar(ft.Text(f"已將【{item['name']}{note_msg} x{modal_qty}】加入購物車！"), duration=1000)
            page.snack_bar.open = True
            page.update()

        modal_submit_btn = ft.ElevatedButton(
            f"放入購物車 • NT${item['price']}",
            style=ft.ButtonStyle(bgcolor="#D35400", color="white", shape=ft.RoundedRectangleBorder(radius=8)),
            on_click=add_modal_to_cart,
            height=45,
            expand=True
        )

        modal_dialog = ft.AlertDialog(
            content_padding=0,
            content=ft.Container(
                content=ft.Column([
                    food_visual(item, width=360, height=180, emoji_size=60,
                                border_radius=ft.border_radius.only(top_left=12, top_right=12)),
                    ft.Container(content=ft.Column([
                        ft.Text(item["name"], size=20, weight="bold", color="#222222"),
                        ft.Text(f"NT${item['price']}", size=16, color="#D35400", weight="bold"),
                        ft.Text(item.get("desc", ""), size=13, color="#666666"),
                        ft.Container(height=4),
                        note_field,
                    ]), padding=15),
                    ft.Divider(height=1),
                    ft.Container(content=ft.Row([
                        ft.Row([
                            ft.IconButton("remove", icon_color="#D35400", on_click=lambda e: update_modal_qty(-1)),
                            qty_text,
                            ft.IconButton("add", icon_color="#D35400", on_click=lambda e: update_modal_qty(1)),
                        ]),
                        modal_submit_btn
                    ], spacing=10), padding=15)
                ], tight=True), width=360, border_radius=12
            )
        )
        page.open(modal_dialog)

    def with_hot_badge(item, visual):
        """熱銷品項在照片左上角加上「🔥 熱銷 No.x」標籤"""
        if item["id"] not in best_sellers:
            return visual
        rank = best_sellers.index(item["id"]) + 1
        badge = ft.Container(
            content=ft.Text(f"🔥 熱銷 No.{rank}", size=11, weight="bold", color="white"),
            bgcolor="#E53935", border_radius=10,
            padding=ft.padding.symmetric(horizontal=8, vertical=3),
            left=6, top=6,
        )
        return ft.Stack([visual, badge], width=160, height=100)

    def create_food_card(item):
        # expand=True：佔滿價格下方剩下的白色空間，按鈕在其中上下左右置中
        stepper = ft.Container(expand=True, alignment=ft.alignment.center)
        small_btn = dict(icon_size=16, width=30, height=30, style=ft.ButtonStyle(padding=0))

        def render_stepper():
            qty = card_qty(item["id"])
            if qty == 0:
                stepper.content = ft.IconButton(
                    "add", icon_color="white", bgcolor="#D35400", tooltip="加入購物車",
                    on_click=lambda e: set_card_qty(item, 1), **small_btn,
                )
            else:
                stepper.content = ft.Container(
                    content=ft.Row([
                        ft.IconButton("delete_outline" if qty == 1 else "remove",
                                      icon_color="red600" if qty == 1 else "#D35400",
                                      on_click=lambda e: set_card_qty(item, card_qty(item["id"]) - 1), **small_btn),
                        ft.Text(str(qty), size=14, weight="bold", color="#222222"),
                        ft.IconButton("add", icon_color="#D35400",
                                      on_click=lambda e: set_card_qty(item, card_qty(item["id"]) + 1), **small_btn),
                    ], spacing=4, tight=True),
                    border=ft.border.all(1, "#E0E0E0"), border_radius=20,
                    padding=ft.padding.symmetric(horizontal=2),
                )

        render_stepper()
        stepper_refreshers[item["id"]] = render_stepper

        return ft.Card(
            elevation=1,
            content=ft.Container(
                content=ft.Column([
                    with_hot_badge(item, food_visual(item, width=160, height=100, emoji_size=45,
                                border_radius=ft.border_radius.only(top_left=8, top_right=8))),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(item["name"], size=14, weight="bold", color="#222222", no_wrap=True),
                            ft.Text(f"NT${item['price']}", size=13, color="#D35400", weight="bold"),
                            stepper,
                        ], spacing=2, expand=True),
                        padding=ft.padding.only(left=8, right=8, top=6, bottom=4),
                        expand=True,
                    ),
                ], spacing=0),
                width=160, height=215, bgcolor="white", border_radius=8,
                on_click=lambda e, i=item: open_item_modal(i)  # 點卡片其他地方仍開啟小視窗（可填備註）
            )
        )

    grid_view = ft.GridView(expand=True, max_extent=180, child_aspect_ratio=0.88, spacing=12, run_spacing=12, padding=12)

    def refresh_grid(category):
        nonlocal current_category
        current_category = category
        grid_view.controls.clear()
        stepper_refreshers.clear()
        # 有輸入關鍵字時先搜尋，再依目前分類篩選
        if search_keyword:
            filtered = [i for i in search_menu(search_keyword)
                        if category == "全部" or i["category"] == category]
        else:
            filtered = get_menu(category)
        for item in filtered:
            grid_view.controls.append(create_food_card(item))
        result_text.value = f"找不到「{search_keyword}」相關餐點" if not filtered else ""
        result_text.visible = not filtered
        render_category_row()
        page.update()

    def on_search(e):
        nonlocal search_keyword
        search_keyword = (e.control.value or "").strip()
        refresh_grid(current_category)

    search_field = ft.TextField(
        hint_text="搜尋餐點，例如：雞、豆腐、辣",
        prefix_icon="search",
        on_change=on_search,
        dense=True,
        border_radius=20,
        border_color="#E0E0E0",
        focused_border_color="#D35400",
        color="#222222",
        text_size=14,
    )
    result_text = ft.Text("", size=14, color="#888888", visible=False)

    categories = get_categories()  # 依 menu.json 自動產生，新增分類不用改這裡
    category_row = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=8)

    def render_category_row():
        category_row.controls.clear()
        for cat in categories:
            is_selected = (cat == current_category)
            btn = ft.Container(
                content=ft.Text(cat, color="white" if is_selected else "#333333", weight="bold" if is_selected else "normal"),
                bgcolor="#D35400" if is_selected else "#F5F5F5",
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                border_radius=20,
                on_click=lambda e, c=cat: refresh_grid(c)
            )
            category_row.controls.append(btn)

    left_menu_panel = ft.Column([
        ft.Container(content=search_field, padding=ft.padding.only(left=10, top=10, right=10)),
        ft.Container(content=category_row, padding=ft.padding.only(left=10, right=10)),
        ft.Container(content=result_text, padding=ft.padding.only(left=14)),
        grid_view
    ], expand=7)

    refresh_grid("全部")

    return ft.View(
        "/",
        appbar=get_appbar("台灣鹽酥雞 (Foodpanda 合作店家)", page),
        controls=[
            ft.Container(
                content=ft.Row([
                    left_menu_panel,
                    cart_sidebar_ui
                ], expand=True, spacing=15),  # 菜單與購物車之間拉開 15px 間距
                padding=ft.padding.symmetric(horizontal=20, vertical=15),  # 網頁整體四周留白 20px
                expand=True
            )
        ],
        padding=0,
        spacing=0
    )