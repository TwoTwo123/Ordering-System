# scripts/make_fake_orders.py（組員 B）
# 產生假歷史訂單給 D 測試「一起購買統計」推薦
# 用法（在專案根目錄執行）：python scripts/make_fake_orders.py
# 會覆蓋 data/orders.json，格式與 receipt_view.py 存的正式訂單相同
import json
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from services.menu_service import get_menu, get_item  # noqa: E402
from services.pricing import calc_price  # noqa: E402

N_ORDERS = 100
random.seed(42)  # 固定亂數種子，每次產生的結果都一樣，方便大家對照

# 刻意埋入的搭配規律，D 的統計應該要能找出來
COMBOS = [
    # 招牌單品：決定熱銷排行（無骨鹽酥雞 > 超大雞排 > 甜不辣）
    (["A01"], 0.60),          # 無骨鹽酥雞
    (["A02"], 0.45),          # 超大雞排
    (["A03"], 0.35),          # 甜不辣
    # 常見搭配：給 D 的「一起購買統計」推薦用
    (["A01", "C01"], 0.25),   # 鹽酥雞 + 四季豆
    (["A01", "E02"], 0.15),   # 鹽酥雞 + 古早味紅茶
    (["A02", "E01"], 0.12),   # 雞排 + 可樂
    (["A03", "A04"], 0.15),   # 甜不辣 + 魷魚
    (["A06", "A09"], 0.15),   # 米血糕 + 豆干
    (["A02", "E04"], 0.10),   # 雞排 + 台灣啤酒
    (["D02", "E02"], 0.12),   # 地瓜球 + 古早味紅茶
    (["F01", "E01"], 0.08),   # 雙人套餐 + 可樂
]


def build_items(menu):
    chosen = {}
    for ids, prob in COMBOS:
        if random.random() < prob:
            for item_id in ids:
                chosen[item_id] = chosen.get(item_id, 0) + 1
    # 再隨機加 0～2 項，讓資料不會太整齊
    for item in random.sample(menu, k=random.randint(0, 2)):
        chosen[item["id"]] = chosen.get(item["id"], 0) + 1
    if not chosen:  # 保證每筆訂單至少有一項
        chosen[random.choice(menu)["id"]] = 1
    return [{"item": get_item(i), "qty": q} for i, q in chosen.items()]


def make_order(n, created):
    items = build_items(get_menu())
    pricing = calc_price(items)
    dining = random.choice(["外送", "內用", "外帶"])
    return {
        "order_id": f"ORD-{created:%Y%m%d}-{1000 + n}",
        "created_at": created.strftime("%Y-%m-%d %H:%M:%S"),
        "dining_type": dining,
        "payment_method": random.choice(["LINE Pay", "現金", "信用卡"]),
        "address": "台北市測試路 1 號" if dining == "外送" else "",
        "table_no": str(random.randint(1, 12)) if dining == "內用" else "",
        "phone": "",
        "note": "",
        "items": items,
        "subtotal": pricing["subtotal"],
        "discount": pricing["discount"],
        "total": pricing["total"],
    }


def main():
    start = datetime(2026, 9, 15, 11, 0)
    orders = []
    for n in range(N_ORDERS):
        created = start + timedelta(days=random.randint(0, 29),
                                    hours=random.randint(0, 11),
                                    minutes=random.randint(0, 59))
        orders.append(make_order(n, created))
    orders.sort(key=lambda o: o["created_at"])

    out = ROOT / "data" / "orders.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)
    print(f"已產生 {len(orders)} 筆假訂單 -> {out}")


if __name__ == "__main__":
    main()
