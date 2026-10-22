# components/layout.py
import flet as ft

def get_appbar(title_text: str, page: ft.Page, show_back: bool = False):
    """
    頂部 Header：
    - 右上角：白色圓形大頭貼與下拉選單
    - 左上角：可選返回箭頭 (返回點餐主頁)
    """
    def on_select(e):
        if e.control.data == "history":
            page.go("/history")
        elif e.control.data == "menu":
            page.go("/")

    user_avatar_menu = ft.PopupMenuButton(
        content=ft.Container(
            content=ft.Icon(ft.Icons.PERSON, color="#D35400", size=20),
            bgcolor="white",
            shape=ft.BoxShape.CIRCLE,
            width=36,
            height=36,
            alignment=ft.alignment.center,
            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.BLACK12)
        ),
        items=[
            ft.PopupMenuItem(
                content=ft.Row([
                    ft.Icon(ft.Icons.RESTAURANT_MENU, size=18, color="#333333"),
                    ft.Text("菜單點餐", size=14, color="#333333")
                ], spacing=10),
                data="menu",
                on_click=on_select
            ),
            ft.PopupMenuItem(
                content=ft.Row([
                    ft.Icon(ft.Icons.RECEIPT_LONG, size=18, color="#333333"),
                    ft.Text("購買紀錄", size=14, color="#333333")
                ], spacing=10),
                data="history",
                on_click=on_select
            ),
        ],
        tooltip="個人選單"
    )

    leading_button = ft.IconButton(
        icon=ft.Icons.ARROW_BACK,
        icon_color="white",
        on_click=lambda e: page.go("/")
    ) if show_back else None

    return ft.AppBar(
        title=ft.Text(title_text, weight="bold", color="white", size=20),
        bgcolor="#D35400",
        center_title=False,
        leading=leading_button,
        actions=[
            ft.Container(
                content=user_avatar_menu,
                padding=ft.padding.only(right=20)
            )
        ]
    )

get_header = get_appbar
get_navbar = lambda page, current_index=0: None
get_bottom_navbar = get_navbar