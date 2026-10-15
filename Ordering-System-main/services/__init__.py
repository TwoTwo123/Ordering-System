# 整合用，統一匯出介面
# 把各個檔案的函式匯入到這裡
from .menu_service import get_menu, search_menu
from .order_service import save_order, list_orders
from .cart_service import add_item, update_qty, remove_item
from .pricing import calc_price
from .recommender import recommend

# 宣告當其他人從 services import * 時，可以拿到哪些東西
__all__ = [
    "get_menu",
    "search_menu",
    "save_order",
    "list_orders",
    "add_item",
    "update_qty",
    "remove_item",
    "calc_price",
    "recommend"
]