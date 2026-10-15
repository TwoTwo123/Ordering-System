# services/menu_service.py（組員 B）
# 菜單資料統一從 data/menu.json 讀取，其他人一律透過這裡的函式取得菜單
import json
from pathlib import Path

# 以這個檔案的位置找 data 資料夾，不論從哪個目錄執行程式都找得到
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MENU_FILE = DATA_DIR / "menu.json"

_menu_cache = None  # 讀過一次就存起來，不用每次都開檔


def _load_menu():
    global _menu_cache
    if _menu_cache is None:
        with open(MENU_FILE, encoding="utf-8") as f:
            _menu_cache = json.load(f)
    return _menu_cache


def get_menu(category=None):
    """回傳菜單清單；給 category 時只回傳該分類（"全部" 或 None 回傳全部）"""
    menu = _load_menu()
    if category in (None, "全部"):
        return list(menu)
    return [item for item in menu if item["category"] == category]


def get_categories():
    """回傳分類清單，第一個固定是 "全部"，其餘依菜單出現順序"""
    categories = []
    for item in _load_menu():
        if item["category"] not in categories:
            categories.append(item["category"])
    return ["全部"] + categories


def get_item(item_id):
    """依品項編號查詢單一品項，找不到回傳 None"""
    for item in _load_menu():
        if item["id"] == item_id:
            return item
    return None


def search_menu(keyword):
    """依關鍵字搜尋品名、分類與描述；空白關鍵字回傳全部"""
    kw = keyword.strip().lower()
    if not kw:
        return get_menu()
    return [
        item for item in _load_menu()
        if kw in item["name"].lower()
        or kw in item["category"].lower()
        or kw in item.get("desc", "").lower()
    ]
