import pandas as pd
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# 【可修改區域】
# ============================================================

# ⚡ 省錢開關
FORCE_RERUN = False

# PTT 資料路徑
PTT_CSV = os.path.join(HERE, "output", "db2_experience_real.csv")

# Google Maps 評論關鍵字（從 db1_wordcloud.csv 萃取體驗相關詞）
# 這些是從精品獨立咖啡廳評論中出現的體驗關鍵字
GOOGLE_MAPS_EXPERIENCE = {
    "甜點": 40,   # 精品獨立 frequency=12，換算成百分比
    "蛋糕": 33,   # frequency=10
    "氛圍": 13,   # frequency=4
    "座位": 23,   # frequency=7
    "乾淨": 17,   # 連鎖品牌 frequency=5
    "插座": 10,   # 連鎖品牌 frequency=3（與PTT重複，取較高值）
}

# ============================================================
# 以下不需要修改
# ============================================================

def run_merge_experience(output_dir=None):
    """整合 PTT 和 Google Maps 體驗關鍵字"""
    if output_dir is None:
        output_dir = os.path.join(HERE, "output")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "db2_experience_merged.csv")

    # ⚡ 省錢檢查
    if not FORCE_RERUN and os.path.exists(output_path):
        print("\n[Step 7] 偵測到現有資料，跳過整合（省錢模式）")
        print(f"  使用現有檔案：{output_path}")
        print("[Step 7] 跳過！\n")
        return output_path

    print("\n[Step 7] 開始整合 PTT + Google Maps 體驗關鍵字...")

    # 讀取 PTT 資料
    ptt_df = pd.read_csv(PTT_CSV)
    ptt_dict = dict(zip(ptt_df["keyword"], ptt_df["frequency_pct"]))

    # 整合兩個來源（取較高值，避免重複低估）
    merged = {}

    # 先加入 PTT 資料
    for keyword, pct in ptt_dict.items():
        merged[keyword] = {"frequency_pct": pct, "source": "PTT Food板"}

    # 再加入 Google Maps 資料（如果重複取較高值）
    for keyword, pct in GOOGLE_MAPS_EXPERIENCE.items():
        if keyword in merged:
            if pct > merged[keyword]["frequency_pct"]:
                merged[keyword] = {"frequency_pct": pct, "source": "PTT + Google Maps"}
        else:
            merged[keyword] = {"frequency_pct": pct, "source": "Google Maps評論"}

    # 整理成 DataFrame
    results = []
    for keyword, data in merged.items():
        results.append({
            "keyword": keyword,
            "frequency_pct": data["frequency_pct"],
            "category": "體驗因素",
            "source": data["source"]
        })

    # 按頻率排序
    results = [r for r in results if r["frequency_pct"] > 0]
    results.sort(key=lambda x: -x["frequency_pct"])

    df = pd.DataFrame(results)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"  輸出完成：db2_experience_merged.csv（{len(df)} 筆）")
    print("\n  整合後關鍵字頻率：")
    for r in results:
        bar = "█" * (r["frequency_pct"] // 5)
        print(f"  {r['keyword']:<10} {r['frequency_pct']:>3}%  {bar}  [{r['source']}]")

    print("[Step 7] 完成！")
    return output_path

if __name__ == "__main__":
    run_merge_experience()
