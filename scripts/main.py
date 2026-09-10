import os
import step1_clean
import step2_scrape_coffee_shops
import step3_calculate_mrt_distance
from step4_pricing import run_pricing
from step6_ptt import run_ptt

# ============================================================
# API Configuration
# ============================================================
API_KEY = "YOUR_GOOGLE_MAPS_API_KEY"

# ============================================================
# File Paths Configuration
# ============================================================
HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(HERE, "output")

SH_PATH  = os.path.join(HERE, "生豆.csv")
SU_PATH  = os.path.join(HERE, "熟豆.csv")
MRT_PATH = os.path.join(HERE, "臺北捷運車站出入口座標.csv")

SHOPS_RAW_PATH  = os.path.join(OUTPUT_DIR, "coffee_shops_raw.csv")
SHOPS_FINAL_PATH = os.path.join(OUTPUT_DIR, "db2_coffee_shops_with_mrt.csv")

# ============================================================
# 主流程：依序執行三個步驟
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("台灣精品咖啡市場分析 — 資料處理流程")
    print("=" * 50)
    print()

    # Step 1：清洗進口資料 → db1_yearly_trend.csv, db1_country_rank.csv
    step1_clean.run(
        sh_path=SH_PATH,
        su_path=SU_PATH,
        output_dir=OUTPUT_DIR
    )

    # Step 2：爬取 Google Maps 咖啡廳資料 → coffee_shops_raw.csv
    step2_scrape_coffee_shops.run(
        api_key=API_KEY,
        output_path=SHOPS_RAW_PATH
    )

    # Step 3：計算捷運距離 → db2_coffee_shops_with_mrt.csv
    step3_calculate_mrt_distance.run(
        shops_path=SHOPS_RAW_PATH,
        mrt_path=MRT_PATH,
        output_path=SHOPS_FINAL_PATH
    )

    # Step 4：建立競品定價資料
    run_pricing(output_dir=OUTPUT_DIR)

    # Step 6：爬取 PTT 體驗關鍵字
    run_ptt(output_dir=OUTPUT_DIR)

    print("=" * 50)
    print("所有步驟完成！output 資料夾內的檔案：")
    for f in os.listdir(OUTPUT_DIR):
        print(f"  - {f}")
    print("=" * 50)