# services/recommender.py（組員 D：推薦系統）
#
# 推薦資料來源：data/orders.json（購買紀錄頁顯示的訂單）
#
# 三個推薦名額，依序由下列來源填入：
#   1. 搭配推薦：從訂單算出「一起購買」的關聯規則，依「提升度 lift」排序，購物車每個品項輪流推薦
#   2. 飲料名額：購物車還沒有飲料時（包含購物車是空的），保留 1 個名額推薦飲料，理由前面標 🥤
#   3. 人氣餐點：以上都不夠時，用熱銷品補滿（購物車是空的時候也是推薦熱銷品）
#
# 關聯規則的三個指標（以 A → B 為例）：
#   support    = A 和 B 一起出現的訂單數
#   confidence = 點 A 的訂單中，也點 B 的比例
#   lift       = confidence ÷ B 平常被點的比例；> 1 代表「點了 A 之後比平常更常點 B」
#   只看 confidence 會一直推薦本來就熱門的品項，所以排序改用 lift
#
# 規則來源：有 data/accosiation.pkl（Apriori 事先算好）就用它，否則從訂單即時計算
#
# 對外函式：
#   recommend_items(cart_items, top_n=3) -> [{"item": 品項, "reason": 理由, "kind": 種類, "score": 分數}, ...]
#   recommend(cart_items)                -> 舊介面，回傳 Flet Text 清單（保留給 cart_view 相容用）
from collections import Counter
from itertools import combinations

from services.menu_service import DATA_DIR, get_item, get_menu
from services.order_service import list_orders, get_best_sellers, ORDERS_FILE

ACCOSIATION_FILE = DATA_DIR / "accosiation.pkl"

MIN_SUPPORT_COUNT = 3     # 至少一起出現幾次才算規則，避免巧合
MIN_CONFIDENCE = 0.20     # 信賴度門檻
MIN_LIFT = 1.0            # 提升度要大於 1 才算有關聯
DRINK_CATEGORY = "飲料類"


def extract_cart(cart_items: list) -> list:
    """從購物車提取商品 ID 列表（不重複，依加入順序）"""
    ids = []
    for entry in cart_items or []:
        item = entry.get("item", entry)
        item_id = item.get("id") if isinstance(item, dict) else getattr(item, "id", None)
        if item_id and str(item_id) not in ids:
            ids.append(str(item_id))
    return ids


def _to_id_set(value) -> set:
    """規則欄位可能是 frozenset（mlxtend 產生）或 "A01,A02" 字串，統一轉成編號集合"""
    if isinstance(value, (set, frozenset, list, tuple)):
        return {str(v).strip() for v in value}
    return {v.strip() for v in str(value).split(",") if v.strip()}


# ---------- 規則來源 1：Apriori 產生的 .pkl ----------
def _rules_from_pickle():
    """讀取 accosiation.pkl，回傳 [(前項集合, 後項集合, confidence, lift), ...]；讀不到回傳 None"""
    if not ACCOSIATION_FILE.exists():
        return None
    try:
        import pandas as pd  # 只有在有 .pkl 時才需要 pandas
        df = pd.read_pickle(ACCOSIATION_FILE)
        rules = []
        for _, r in df.iterrows():
            conf = float(r.get("confidence", 0.5))
            lift = float(r.get("lift", 1.0)) if "lift" in r else 1.0
            rules.append((_to_id_set(r["antecedents"]), _to_id_set(r["consequents"]), conf, lift))
        return rules
    except Exception as e:
        print(f"【推薦系統】讀取 {ACCOSIATION_FILE.name} 失敗，改用訂單即時計算：{e}")
        return None


# ---------- 規則來源 2：從訂單即時計算 ----------
def _rules_from_orders():
    orders = list_orders()
    total = len(orders) or 1
    item_count = Counter()
    pair_count = Counter()
    for order in orders:
        ids = sorted({str(e["item"]["id"]) for e in order.get("items", [])
                      if isinstance(e.get("item"), dict) and e["item"].get("id")})
        item_count.update(ids)
        pair_count.update(combinations(ids, 2))

    rules = []
    for (a, b), together in pair_count.items():
        if together < MIN_SUPPORT_COUNT:
            continue
        for x, y in ((a, b), (b, a)):
            conf = together / item_count[x]
            lift = conf / (item_count[y] / total)
            if conf >= MIN_CONFIDENCE and lift > MIN_LIFT:
                rules.append(({x}, {y}, conf, lift))
    return rules


_rules_cache = None
_rules_stamp = None


def _data_stamp():
    """訂單檔的修改時間；有新訂單存進去時會改變"""
    return tuple(f.stat().st_mtime if f.exists() else 0
                 for f in (ORDERS_FILE, ACCOSIATION_FILE))


def _get_rules():
    """規則會快取起來，訂單檔有變動（例如剛結帳）時自動重新計算"""
    global _rules_cache, _rules_stamp
    stamp = _data_stamp()
    if _rules_cache is None or stamp != _rules_stamp:
        _rules_cache = _rules_from_pickle() or _rules_from_orders()
        _rules_stamp = stamp
    return _rules_cache


def reload_rules():
    """新訂單存進去後呼叫，讓推薦重新計算"""
    global _rules_cache
    _rules_cache = None


def _is_drink(item_id):
    item = get_item(item_id)
    return bool(item) and item.get("category") == DRINK_CATEGORY


# ---------- 各來源的候選 ----------
def _association_candidates(cart_ids, exclude):
    """搭配推薦：購物車每個品項輪流取 lift 最高的搭配，從最後加入的品項開始"""
    in_cart = set(cart_ids)
    per_source = {}
    for antecedents, consequents, conf, lift in _get_rules():
        if not antecedents.issubset(in_cart):
            continue
        source = cart_ids[max(cart_ids.index(a) for a in antecedents)]
        for target in consequents - in_cart:
            per_source.setdefault(source, []).append((lift, conf, target))
    for cands in per_source.values():
        cands.sort(reverse=True)

    results, seen = [], set(exclude)
    order = [i for i in reversed(cart_ids) if i in per_source]
    while any(per_source[s] for s in order):
        for source in order:
            while per_source[source]:
                lift, conf, target = per_source[source].pop(0)
                if target not in seen:
                    src = get_item(source)
                    src_name = src["name"] if src else "這道餐"
                    results.append((target, f"點「{src_name}」的人有 {conf:.0%} 也點了", lift))
                    seen.add(target)
                    break
    return results


def _drink_candidates(exclude, associations):
    """飲料名額：優先搭配推薦中的飲料 → 最熱銷的飲料"""
    for i, reason, _ in associations:
        if _is_drink(i) and i not in exclude:
            return (i, f"🥤 {reason}")
    for i in get_best_sellers(len(get_menu())):
        if _is_drink(i) and i not in exclude:
            return (i, "🥤 人氣飲料，配炸物解膩")
    return None


# ---------- 對外主函式 ----------
def recommend_items(cart_items: list, top_n: int = 3) -> list:
    cart_ids = extract_cart(cart_items)
    in_cart = set(cart_ids)
    picked = []           # [(品項編號, 理由, 種類, 分數)]
    used = set(in_cart)

    def take(item_id, reason, kind, score=0.0):
        picked.append((item_id, reason, kind, score))
        used.add(item_id)

    associations = _association_candidates(cart_ids, used) if cart_ids else []
    need_drink = not any(_is_drink(i) for i in cart_ids)  # 購物車沒有飲料（含空購物車）

    # 1. 搭配推薦，若需要飲料就先保留最後一個名額
    slots_for_assoc = top_n - len(picked) - (1 if need_drink else 0)
    for item_id, reason, lift in associations:
        if slots_for_assoc <= 0:
            break
        if item_id in used:
            continue
        if _is_drink(item_id) and need_drink:
            take(item_id, f"🥤 {reason}", "drink", round(lift, 2))
            need_drink = False  # 已經推到飲料了，保留的名額還給搭配推薦
            continue
        take(item_id, reason, "association", round(lift, 2))
        slots_for_assoc -= 1

    # 2. 飲料名額
    if need_drink and len(picked) < top_n:
        drink = _drink_candidates(used, associations)
        if drink:
            take(drink[0], drink[1], "drink")

    # 3. 還有空位：剩下的搭配推薦 → 人氣餐點
    for item_id, reason, lift in associations:
        if len(picked) >= top_n:
            break
        if item_id not in used:
            take(item_id, reason, "association", round(lift, 2))
    for item_id in get_best_sellers(len(get_menu())):
        if len(picked) >= top_n:
            break
        if item_id not in used:
            take(item_id, "🔥 人氣餐點", "popular")

    # 飲料固定排在最後一個，畫面比較整齊
    picked = [p for p in picked if p[2] != "drink"] + [p for p in picked if p[2] == "drink"]

    output = []
    for item_id, reason, kind, score in picked[:top_n]:
        item = get_item(item_id)
        if item:  # 規則裡若有已下架的品項就略過
            output.append({"item": item, "reason": reason, "kind": kind, "score": score})
    return output


def recommend(cart_items: list = None) -> list:
    """舊介面：回傳 Flet Text 清單，供 cart_view.py 使用"""
    from flet import Text
    recs = recommend_items(cart_items or [])
    if not extract_cart(cart_items or []):
        return [
            Text("💡 推薦搭配:", size=14, color="brown700", weight="bold"),
            Text("購物車內尚無餐點，加入餐點即刻解鎖智能推薦！", size=12, color="grey600"),
        ]
    names = "、".join(r["item"]["name"] for r in recs) or "熱門餐點"
    return [
        Text("💡 智能推薦搭配:", size=14, color="brown700", weight="bold"),
        Text(f"點這道餐的人也喜歡：{names}", size=13, color="brown900", weight="bold"),
    ]
