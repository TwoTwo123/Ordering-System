# views/menu_view.py
import flet as ft
from services.cart_service import add_item
from components.cart_sidebar import create_cart_sidebar
from services.menu_service import get_menu, get_categories  # 菜單資料改由組員 B 的服務提供（data/menu.json）

def menu_view(page: ft.Page):
    """菜單主頁 View"""
    current_category = "全部"
    cart_sidebar_ui, refresh_cart = create_cart_sidebar(page)

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

        def add_modal_to_cart(e):
            for _ in range(modal_qty):
                add_item(item)
            refresh_cart()
            page.close(modal_dialog)
            page.snack_bar = ft.SnackBar(ft.Text(f"已將【{item['name']} x{modal_qty}】加入購物車！"), duration=1000)
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
                    ft.Container(content=ft.Text(item["img"], size=60), alignment=ft.alignment.center, height=140, bgcolor="#FEF5ED"),
                    ft.Container(content=ft.Column([
                        ft.Text(item["name"], size=20, weight="bold", color="#222222"),
                        ft.Text(f"NT${item['price']}", size=16, color="#D35400", weight="bold"),
                        ft.Text(item.get("desc", ""), size=13, color="#666666"),
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

    def create_food_card(item):
        return ft.Card(
            elevation=1,
            content=ft.Container(
                content=ft.Column([
                    ft.Container(content=ft.Text(item["img"], size=45), alignment=ft.alignment.center, height=100, bgcolor="#FEF5ED", border_radius=ft.border_radius.only(top_left=8, top_right=8)),
                    ft.Container(content=ft.Column([
                        ft.Text(item["name"], size=14, weight="bold", color="#222222", no_wrap=True),
                        ft.Text(f"NT${item['price']}", size=13, color="#D35400", weight="bold"),
                    ], spacing=2), padding=ft.padding.all(8)),
                ]),
                width=160, height=165, bgcolor="white", border_radius=8,
                on_click=lambda e, i=item: open_item_modal(i)
            )
        )

    grid_view = ft.GridView(expand=True, max_extent=180, child_aspect_ratio=0.8, spacing=12, run_spacing=12, padding=10)

    def refresh_grid(category):
        nonlocal current_category
        current_category = category
        grid_view.controls.clear()
        filtered = get_menu(category)
        for item in filtered:
            grid_view.controls.append(create_food_card(item))
        render_category_row()
        page.update()

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
        ft.Container(content=category_row, padding=ft.padding.only(left=10, top=10, right=10)),
        grid_view
    ], expand=7)

    refresh_grid("全部")

    return ft.View(
        "/",
        controls=[
            ft.AppBar(title=ft.Text("🐼 台灣鹽酥雞 (Foodpanda 合作店家)", size=20, weight="bold", color="white"), bgcolor="#D35400"),
            ft.Row([
                left_menu_panel,
                cart_sidebar_ui
            ], expand=True, spacing=0)
        ]
    )