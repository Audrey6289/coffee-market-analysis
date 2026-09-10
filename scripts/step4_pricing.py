import pandas as pd
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# 【可修改區域】更新競品定價時只需修改這裡
# 資料來源：各品牌門市實地查詢 / Google Maps（2026年4月）
# ============================================================

PRICING_DATA = [
    {"brand": "星巴克",  "product": "美式", "price": 95,  "size": "中杯", "positioning": "國際連鎖高價"},
    {"brand": "星巴克",  "product": "拿鐵", "price": 120, "size": "中杯", "positioning": "國際連鎖高價"},
    {"brand": "路易莎",  "product": "美式", "price": 60,  "size": "中杯", "positioning": "本土平價"},
    {"brand": "路易莎",  "product": "拿鐵", "price": 80,  "size": "中杯", "positioning": "本土平價"},
    {"brand": "cama",   "product": "美式", "price": 65,  "size": "中杯", "positioning": "本土外帶"},
    {"brand": "cama",   "product": "拿鐵", "price": 85,  "size": "中杯", "positioning": "本土外帶"},
    {"brand": "丹堤",   "product": "美式", "price": 80,  "size": "大杯(無中杯)", "positioning": "老牌餐食複合"},
    {"brand": "丹堤",   "product": "拿鐵", "price": 105, "size": "大杯(無中杯)", "positioning": "老牌餐食複合"},
    {"brand": "西雅圖", "product": "美式", "price": 100, "size": "中杯", "positioning": "重烘焙中高價"},
    {"brand": "西雅圖", "product": "拿鐵", "price": 120, "size": "中杯", "positioning": "重烘焙中高價"},
    {"brand": "客美多", "product": "美式", "price": 120, "size": "中杯", "positioning": "日系複合"},
    {"brand": "客美多", "product": "拿鐵", "price": 140, "size": "中杯", "positioning": "日系複合"},
    {"brand": "湛盧",   "product": "美式", "price": 240, "size": "不分杯型", "positioning": "精品旗艦"},
    {"brand": "湛盧",   "product": "拿鐵", "price": 240, "size": "不分杯型", "positioning": "精品旗艦"},
    {"brand": "CAFE!N", "product": "美式", "price": 60,  "size": "M杯", "positioning": "新興精品平價"},
    {"brand": "CAFE!N", "product": "拿鐵", "price": 100, "size": "M杯", "positioning": "新興精品平價"},
]

# ============================================================
# 驗證規則（確保資料品質）
# ============================================================

# 合理價格區間（元）
PRICE_MIN = 40
PRICE_MAX = 500

# 必須包含的品牌
REQUIRED_BRANDS = {"星巴克", "路易莎", "cama", "丹堤", "西雅圖", "客美多", "湛盧", "CAFE!N"}

# 必須包含的品項
REQUIRED_PRODUCTS = {"美式", "拿鐵"}

def validate(data):
    """驗證定價資料品質"""
    errors = []
    df = pd.DataFrame(data)

    # 檢查價格是否在合理區間
    out_of_range = df[(df["price"] < PRICE_MIN) | (df["price"] > PRICE_MAX)]
    if not out_of_range.empty:
        for _, row in out_of_range.iterrows():
            errors.append(f"價格異常：{row['brand']} {row['product']} = {row['price']} 元（區間：{PRICE_MIN}~{PRICE_MAX}）")

    # 檢查品牌是否完整
    actual_brands = set(df["brand"].unique())
    missing_brands = REQUIRED_BRANDS - actual_brands
    if missing_brands:
        errors.append(f"缺少品牌：{missing_brands}")

    # 檢查每個品牌是否都有美式和拿鐵
    for brand in REQUIRED_BRANDS:
        brand_df = df[df["brand"] == brand]
        missing_products = REQUIRED_PRODUCTS - set(brand_df["product"].unique())
        if missing_products:
            errors.append(f"{brand} 缺少品項：{missing_products}")

    return errors

def run_pricing(output_dir=None):
    """建立競品定價資料，產出 db2_pricing_real.csv"""
    print("\n[Step 4] 開始建立競品定價資料...")

    if output_dir is None:
        output_dir = os.path.join(HERE, "output")
    os.makedirs(output_dir, exist_ok=True)

    # 驗證資料
    errors = validate(PRICING_DATA)
    if errors:
        print("  ⚠️  發現資料問題：")
        for e in errors:
            print(f"     - {e}")
        print("  請修正後重新執行！")
        return
    else:
        print("  ✅ 資料驗證通過！")

    # 輸出 CSV
    df = pd.DataFrame(PRICING_DATA)
    output_path = os.path.join(output_dir, "db2_pricing_real.csv")
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"  輸出完成：db2_pricing_real.csv（{len(df)} 筆）")
    print("\n  定價摘要：")
    print(f"  {'品牌':<10} {'美式':>6} {'拿鐵':>6}  定位")
    print("  " + "-" * 45)
    for brand in REQUIRED_BRANDS:
        brand_data = [r for r in PRICING_DATA if r["brand"] == brand]
        americano = next((r["price"] for r in brand_data if r["product"] == "美式"), "-")
        latte = next((r["price"] for r in brand_data if r["product"] == "拿鐵"), "-")
        positioning = next((r["positioning"] for r in brand_data), "-")
        print(f"  {brand:<10} {americano:>6} {latte:>6}  {positioning}")

    print("[Step 4] 完成！")
    return output_path

if __name__ == "__main__":
    run_pricing()