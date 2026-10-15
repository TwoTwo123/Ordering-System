import flet as ft

# 定義整個 App 的主題設定
app_theme = ft.Theme(
    # 這裡可以改主色系，例如 "red", "green", "orange"
    color_scheme_seed="blue", 
    
    # 調整預設字級，確保在手機上不會太小
    text_theme=ft.TextTheme(
        body_large=ft.TextStyle(size=18), 
        body_medium=ft.TextStyle(size=16),
        title_large=ft.TextStyle(size=22, weight=ft.FontWeight.BOLD),
    )
)