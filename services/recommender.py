from flet import Text
from pickle import dump as p_dump, load as p_load
from json import load

from pandas import DataFrame, crosstab, read_pickle

from services.menu_service import DATA_DIR

ORDER_FILE = DATA_DIR / "orders_restructured"
ACCOSIATION_FILE = DATA_DIR / "accosiation.pkl"


def recommend(cart_items: list = []) -> list[Text]:
  """依購物車內容回傳推薦品項"""
  rmder = recommender()
  cart = mapping_menu(rmder.get_recommendation(extract_cart(cart_items)))

  
  return [Text("💡 推薦搭配：", size=12, color="brown700", weight="bold"),
          Text(f"{cart[0]}, {cart[1]}, {cart[2]}", size=13, color="brown900")]



def extract_cart(cart_items: list[dict]) -> list[str]:

  item_id_list = []

  for item in cart_items:
    item_id_list.append(item["item"]["id"])

  return item_id_list



def mapping_menu(cart_items: list[str]):
  for idx, items in enumerate(cart_items):
    cart_items[idx] = binary_search(items)

  return cart_items



def binary_search(target: str) -> str:
  try:
    with open(DATA_DIR / "menu.json", encoding="utf8") as f:
      menu = load(f)

  except Exception as e:
    print(e)

  length = len(menu)

  left = 0
  right = length - 1

  while left <= right:
    mid = left + right >> 1

    if menu[mid]["id"] == target:
      return menu[mid]["name"]

    if menu[mid]["id"] < target:
      left = mid + 1
    else:
      right = mid - 1

  return ""



class recommender:

  def __init__(self):
      pass



  def get_recommendation(self, cart_items: list[str]):
    
    recommendations = self.__recommend_by_apriori(cart_items, read_pickle(ACCOSIATION_FILE))
    return recommendations["index"].to_list()


  
  def __recommend_by_apriori(
      self, selected_items: list, association_rules_df: DataFrame,
      top_n=3, min_confidence=0.3, min_lift=1.0
  ):
    """
    根據 Apriori 關聯規則推薦餐點。

    Parameters
    ----------
    selected_items : list
        顧客已選擇的餐點。
    association_rules_df : pandas.DataFrame
        analyze_item_association() 回傳的關聯規則。
    top_n : int
        推薦品項數量。
    min_confidence : float
        最低信賴度。
    min_lift : float
        最低提升度。

    Returns
    -------
    pandas.DataFrame
        推薦品項與推薦分數。
    
    `recommendation_score`：目前用 confidence × lift 計算的排序分數，越高越優先推薦；它不是購買機率。

    `confidence`：顧客購買前項時，也購買推薦品項的比例。

    `lift`：衡量兩者的關聯程度，越大通常表示正向關聯越強。

    `support`：這組品項在所有訂單中的出現比例。
    """
    columns = [
      "item_name",
      "recommendation_score",
      "confidence",
      "lift",
      "support"
    ]
    
    if not selected_items:
        raise ValueError("請至少選擇一個餐點")

    if top_n < 1:
        raise ValueError("top_n 必須大於 0")

    if association_rules_df.empty:
        return DataFrame(columns=columns)

    required_columns = {
        "antecedents",
        "consequents",
        "confidence",
        "lift",
        "support"
    }

    if not required_columns.issubset(association_rules_df.columns):
      raise ValueError("關聯規則缺少必要欄位")

    selected_items=set(selected_items)
    scores = {}

    for _, rule in association_rules_df.iterrows():
      antecedents = set(
        rule["antecedents"].split(", ")
      )
      consequents = set(
        rule["consequents"].split(", ")
      )

      if not antecedents.issubset(selected_items):
        continue

      confidence = float(rule["confidence"])
      lift = float(rule["lift"])
      support = float(rule["support"])

      if confidence < min_confidence or lift < min_lift:
        continue

      candidates = consequents - selected_items

      for item in candidates:
        if item not in scores:
          scores[item] = {
            "recommendation_score": 0.0,
            "confidence": 0.0,
            "lift": 0.0,
            "support": 0.0
          }

        score = confidence * lift

        scores[item]["recommendation_score"] = max(
          scores[item]["recommendation_score"],
          score
        )

        scores[item]["confidence"] = max(
          scores[item]["confidence"],
          confidence
        )

        scores[item]["lift"] = max(
          scores[item]["lift"],
          lift
        )

        scores[item]["support"] = max(
          scores[item]["support"],
          support
        )

    if not scores:
      return DataFrame(columns=columns)

    recommendations = DataFrame.from_dict(scores, orient="index")

    return (
      recommendations
      .reset_index()
      .sort_values(
        by=[
          "recommendation_score",
          "confidence",
          "support"
        ],
        ascending=False
      )
      .head(top_n)
      .reset_index(drop=True)
    )



  def __analyze_item_association(
      self, order_item_matrix: DataFrame,
      min_support=0.05, min_confidence=0.3, min_lift=1.0
  ) -> DataFrame:
    """
    使用 Apriori 演算法分析餐廳餐點關聯性。

    Parameters
    ----------
    order_item_matrix : pandas.DataFrame
        訂單 × 品項的二元矩陣，購買為 1，未購買為 0。
    min_support : float
        最低支持度門檻。
    min_confidence : float
        最低信賴度門檻。
    min_lift : float
        最低提升度門檻。

    Returns
    -------
    pandas.DataFrame
        符合條件的關聯規則，依 Lift 由高至低排序。
    """
    from mlxtend.frequent_patterns import apriori, association_rules

    if order_item_matrix.empty:
      raise ValueError("訂單品項矩陣不能為空")

    if not 0 < min_support <= 1:
        raise ValueError("min_support 必須介於 0 和 1 之間")

    if not 0 <= min_confidence <= 1:
        raise ValueError("min_confidence 必須介於 0 和 1 之間")

    if min_lift < 0:
        raise ValueError("min_lift 不可小於 0")

    basket = order_item_matrix.gt(0)

    frequent_itemsets = apriori(basket, min_support, True)

    if frequent_itemsets.empty:
      return DataFrame(
        columns=[
          "antecedents",
          "consequents",
          "support",
          "confidence",
          "lift"
        ]
      )

    rules = association_rules(
      frequent_itemsets,
      metric="confidence",
      min_threshold=min_confidence
    )

    if rules.empty: return rules

    rules = rules[rules["lift"] >= min_lift].copy()

    rules["antecedents"] = rules["antecedents"].apply(
      lambda items: ", ".join(sorted(map(str, items)))
    )

    rules["consequents"] = rules["consequents"].apply(
      lambda items: ", ".join(sorted(map(str, items)))
    )

    rules = rules[
      [
        "antecedents",
        "consequents",
        "support",
        "confidence",
        "lift"
      ]
    ].sort_values(
      by=["lift", "confidence", "support"],
      ascending=False
    ).reset_index(drop=True)

    return rules



  def __create_recommend_matrix(self):

    order_item_matrix = self.__load_orders_restructured()
    association_rules_df = self.__analyze_item_association(order_item_matrix)

    try:
        association_rules_df.to_pickle(ACCOSIATION_FILE)
  
    except Exception as e:
      print(e)



  def __load_orders_restructured(self) -> DataFrame:
    try:
      with open(ORDER_FILE, 'rb') as f:
        df = DataFrame(p_load(f), columns=["order_id", "item_name"]).drop_duplicates(["order_id", "item_name"])

      return crosstab(df["order_id"], df["item_name"])

    except Exception as e:
      print(e)



  def __get_orders_list(self) -> list:
    """存取歷史訂單"""
    try:
      with open(DATA_DIR / "orders.json", encoding="utf8") as f:
        return load(f)
    except:
      return []



  def __restruct_orders_list(self):
    """重構整個歷史訂單記錄提供給統計分析"""
    orders = self.__get_orders_list()
    new_orders = []
    count =0
    for order in orders:
      if count == 5: break
      for item in order["items"]:
        new_orders.append((order["order_id"], item["item"]["id"]))
        count+=1

    try:
      with open(ORDER_FILE, 'wb') as f:
        p_dump(new_orders, f)
    except Exception as e:
      print(e)

    # try:
    #   with open(Path(__file__).resolve().parent.parent / "data/orders_restructured.json", 'w') as f:
    #     dump(new_orders, f)
    # except Exception as e:
    #   print(e)
  


if __name__ == "__main__":
  # recommenderImp.create_recommend_matrix()
  mapping_menu(["A01", "A03", "A07", "B03", "C04", "D01", "F01", "E04"])
