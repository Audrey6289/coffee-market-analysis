"""
ETL Script：Kaggle 咖啡廳銷售資料清理
輸入：Kaggle Coffee Shop 資料集（多個 CSV）
輸出：
  - db3_association_final.csv（飲料 × 烘焙 同購率矩陣）
  - db3_cohort_final.csv（世代留存分析，模擬示意數據）

使用方式：
  1. 將所有 Kaggle CSV 放在同一個資料夾
  2. 修改下方 DATA_DIR / OUTPUT_DIR 為你的實際路徑
  3. 執行：python etl_coffee_kaggle.py
"""

import pandas as pd
import os

# ============================================================
# 設定區：修改這裡的路徑
# ============================================================
DATA_DIR   = r"C:\Users\Vanessa\Desktop\產業尖兵\BI_project\coffee_shop_sales_KAGGLE"
OUTPUT_DIR = r"C:\Users\Vanessa\Desktop\產業尖兵\BI_project\output"

SALES_FILE    = os.path.join(DATA_DIR, "201904 sales reciepts.csv")
PRODUCT_FILE  = os.path.join(DATA_DIR, "product.csv")
CUSTOMER_FILE = os.path.join(DATA_DIR, "customer.csv")

# ============================================================
# STEP 1：載入原始資料
# ============================================================
print("📥 載入原始資料...")
sales    = pd.read_csv(SALES_FILE)
product  = pd.read_csv(PRODUCT_FILE)
customer = pd.read_csv(CUSTOMER_FILE)

print(f"  銷售明細：{len(sales):,} 筆")
print(f"  商品資料：{len(product):,} 筆")
print(f"  顧客資料：{len(customer):,} 筆")

# ============================================================
# STEP 2：資料清理
# ============================================================
print("\n🧹 資料清理...")

# 2-1 銷售資料：移除空值、轉換日期
sales = sales.dropna(subset=['transaction_id', 'product_id', 'customer_id'])
sales['transaction_date'] = pd.to_datetime(sales['transaction_date'])
sales['customer_id'] = sales['customer_id'].astype(int)

# 2-2 商品資料：只保留需要欄位
product = product[['product_id', 'product', 'product_category', 'product_type']].copy()
product = product.dropna(subset=['product_id', 'product'])

# 2-3 顧客資料：轉換日期
customer = customer[['customer_id', 'customer_since']].copy()
customer = customer.dropna()
customer['customer_since'] = pd.to_datetime(customer['customer_since'])

# 2-4 合併商品名稱到銷售資料
df = sales.merge(product, on='product_id', how='left')
print(f"  合併後筆數：{len(df):,}")

# ============================================================
# STEP 3：商品中文名稱對應 & 飲料/烘焙分類
# ============================================================
print("\n🏷️  商品名稱中文化...")

# 英文關鍵字 → 中文名稱對應
name_map = {
    # 咖啡類（飲料）
    'Latte':                     '拿鐵',
    'Cappuccino':                '卡布奇諾',
    'Americano':                 '美式咖啡',
    'Espresso':                  '義式濃縮',
    'Ouro Brasileiro':           '義式濃縮',
    # 單品咖啡（合併為一類）
    'Columbian':                 '單品咖啡',
    'Ethiopia':                  '單品咖啡',
    'Brazilian':                 '單品咖啡',
    'Jamaican':                  '單品咖啡',
    'Our Old Time':              '單品咖啡',
    # 巧克力飲品（飲料）
    'Dark chocolate':            '熱巧克力',
    'Sustainably Grown Organic': '有機可可',
    # 烘焙類（食物）
    'Chocolate Croissant':       '巧克力可頌',
    'Almond Croissant':          '杏仁可頌',
    'Croissant':                 '原味可頌',
    'Ginger Scone':              '薑味司康',
    'Cranberry Scone':           '蔓越莓司康',
    'Jumbo Savory Scone':        '鹹味司康',
    'Scottish Cream Scone':      '奶油司康',
    'Oatmeal Scone':             '燕麥司康',
    'Hazelnut Biscotti':         '榛果脆餅',
    'Chocolate Chip Biscotti':   '巧克力脆餅',
    'Ginger Biscotti':           '薑味脆餅',
}

# 飲料 vs 烘焙分類集合
DRINKS = {'拿鐵', '卡布奇諾', '美式咖啡', '義式濃縮', '單品咖啡', '熱巧克力', '有機可可'}
BAKERY = {'巧克力可頌', '杏仁可頌', '原味可頌', '薑味司康', '蔓越莓司康',
          '鹹味司康', '奶油司康', '燕麥司康', '榛果脆餅', '巧克力脆餅', '薑味脆餅'}

def map_product_name(name):
    for key, zh in name_map.items():
        if key in str(name):
            return zh
    return None

df['product_zh'] = df['product'].apply(map_product_name)
df_filtered = df.dropna(subset=['product_zh']).copy()

print(f"  篩選後筆數：{len(df_filtered):,}")
print(f"  商品分布：\n{df_filtered['product_zh'].value_counts().to_string()}")

# ============================================================
# STEP 4：商品關聯矩陣（飲料 × 烘焙）
# 邏輯：「點了某飲料的人，同時帶了哪些點心？」
# item_a = 飲料，item_b = 烘焙
# ============================================================
print("\n🔗 計算飲料 × 烘焙同購率...")

basket = df_filtered.groupby('transaction_id')['product_zh'].apply(list)
basket_multi = basket[basket.apply(lambda x: len(set(x)) >= 2)]
total_orders = len(basket_multi)
print(f"  多商品訂單數：{total_orders:,}")

pair_rows = []
for items in basket_multi:
    items = list(set(items))
    drink_items  = [i for i in items if i in DRINKS]
    bakery_items = [i for i in items if i in BAKERY]
    for d in drink_items:
        for b in bakery_items:
            pair_rows.append((d, b))

pair_count = {}
for d, b in pair_rows:
    pair_count[(d, b)] = pair_count.get((d, b), 0) + 1

rows = []
for (d, b), count in pair_count.items():
    pct = round(count / total_orders * 100, 1)
    rows.append({'item_a': d, 'item_b': b, 'support_pct': pct})

assoc_df = pd.DataFrame(rows).sort_values('support_pct', ascending=False)

assoc_output = os.path.join(OUTPUT_DIR, "db3_association_final.csv")
assoc_df.to_csv(assoc_output, index=False, encoding='utf-8-sig')
print(f"  ✅ 輸出：{assoc_output}")
print(f"  飲料種類：{assoc_df['item_a'].nunique()} 種")
print(f"  烘焙種類：{assoc_df['item_b'].nunique()} 種")
print(f"  配對組合：{len(assoc_df)} 筆")
print(assoc_df.head(10).to_string(index=False))

# ============================================================
# STEP 5：世代留存分析（Cohort Analysis）
# 注意：此資料集只有一個月交易紀錄，無法計算真實留存率
# 以模擬示意數據呈現，標注「模擬示意數據」
# ============================================================
print("\n📅 產出世代留存率（模擬示意數據）...")

cohort_data = []
campaigns = [
    ('雙11買一送一',  280, [100.0, 67.9, 42.1, 31.1, 25.0, 22.1]),
    ('買二送一活動',  240, [100.0, 70.8, 47.9, 37.1, 28.5, 21.3]),
    ('會員日優惠',    195, [100.0, 65.1, 39.0, 28.4, 19.2, 14.1]),
    ('新品上市嘗鮮',  160, [100.0, 58.1, 34.5, 22.3, 15.6, 11.2]),
    ('集點兌換活動',  210, [100.0, 72.4, 51.2, 40.8, 33.1, 27.6]),
    ('限定季節飲品',  175, [100.0, 63.2, 41.5, 29.7, 21.4, 16.8]),
]
months = ['M0', 'M1', 'M2', 'M3', 'M4', 'M5']

for campaign, base, rates in campaigns:
    for m, r in zip(months, rates):
        cohort_data.append({
            'campaign':       campaign,
            'month_label':    m,
            'base_users':     base,
            'retained_users': round(base * r / 100),
            'retention_pct':  r,
        })

cohort_df = pd.DataFrame(cohort_data)

cohort_output = os.path.join(OUTPUT_DIR, "db3_cohort_final.csv")
cohort_df.to_csv(cohort_output, index=False, encoding='utf-8-sig')
print(f"  ✅ 輸出：{cohort_output}")
print(cohort_df.to_string(index=False))

# ============================================================
# 完成
# ============================================================
print("\n🎉 ETL 完成！")
print(f"  關聯矩陣 → {assoc_output}")
print(f"  世代留存 → {cohort_output}")
print("\n📌 下一步：將這兩個 CSV 載入 Power BI，取代舊版資料來源！")
