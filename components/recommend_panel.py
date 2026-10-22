# components/recommend_panel.py（組員 D：推薦區塊 UI）
# 放在側邊購物車裡，依購物車內容顯示推薦卡片，按「＋」可直接加入購物車
import flet as ft
from pathlib import Path

from services.cart_service import get_cart
from services.recommender import recommend_items

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def _thumb(item):
    photo = item.get("photo")
    if photo and (ASSETS_DIR / photo).exists():
        return ft.Container(
            content=ft.Image(src=photo, width=36, height=36, fit=ft.ImageFit.COVER),
            width=36, height=36, border_radius=6, clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        )
    return ft.Container(
        content=ft.Text(item.get("img", "🍗"), size=20),
        width=36, height=36, bgcolor="#FEF5ED", border_radius=6, alignment=ft.alignment.center,
    )


def create_recommend_panel(on_add):
    """
    on_add(item)：按下推薦卡片的「＋」時呼叫，由購物車負責加入並重新整理
    回傳 (panel 控制項, refresh 函式)
    """
    title = ft.Text("💡 推薦搭配", size=14, weight="bold", color="#8D4004")
    rows = ft.Column(spacing=6)
    panel = ft.Container(
        content=ft.Column([title, rows], spacing=6),
        bgcolor="#FFF8E1",
        border=ft.border.all(1, "#FFE0A3"),
        border_radius=8,
        padding=10,
    )

    def refresh():
        cart = get_cart()
        title.value = "💡 推薦搭配" if cart else "💡 不知道吃什麼？試試熱銷品"
        rows.controls.clear()
        for rec in recommend_items(cart, top_n=3):
            item = rec["item"]
            rows.controls.append(
                ft.Row([
                    _thumb(item),
                    ft.Column([
                        ft.Text(f"{item['name']}  NT${item['price']}", size=13, weight="bold",
                                color="#222222", no_wrap=True),
                        ft.Text(rec["reason"], size=11, color="#8D6E63", no_wrap=True),
                    ], spacing=0, expand=True),
                    ft.IconButton(
                        "add", icon_color="white", bgcolor="#D35400",
                        icon_size=16, width=28, height=28, style=ft.ButtonStyle(padding=0),
                        tooltip="加入購物車",
                        on_click=lambda e, it=item: on_add(it),
                    ),
                ], spacing=8)
            )
        panel.visible = bool(rows.controls)

    refresh()
    return panel, refresh
