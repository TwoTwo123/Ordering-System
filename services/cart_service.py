# 購物車的操作
def add_item(item_id, qty=1):
    """購物車新增項目"""
    print(f"系統：已將商品 {item_id} 加入購物車，數量：{qty}")

def update_qty(item_id, qty):
    """更新購物車商品數量"""
    print(f"系統：已將商品 {item_id} 的數量更新為 {qty}")

def remove_item(item_id):
    """從購物車移除商品"""
    print(f"系統：已將商品 {item_id} 從購物車移除")