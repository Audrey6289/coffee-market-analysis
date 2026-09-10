import pandas as pd
import numpy as np
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# 【可修改區域】
# ============================================================
MRT_INPUT = os.path.join(HERE, "臺北捷運車站出入口座標.csv")

# ⚡ 省錢開關：False = 有舊資料就直接用
#              True  = 強制重新計算
FORCE_RERUN = False

# ============================================================
# 以下不需要修改
# ============================================================

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))

def proximity_label(d):
    if d <= 300:
        return "300m內"
    elif d <= 500:
        return "300-500m"
    else:
        return "500m以上"

def run_mrt(shops_csv, output_dir=None):
    """計算咖啡廳距最近捷運站距離，產出 db2_coffee_shops_with_mrt.csv"""
    if output_dir is None:
        output_dir = os.path.join(HERE, "output")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "db2_coffee_shops_with_mrt.csv")

    # ⚡ 省錢檢查
    if not FORCE_RERUN and os.path.exists(output_path):
        print("\n[Step 3] 偵測到現有資料，跳過計算（省錢模式）")
        print(f"  使用現有檔案：{output_path}")
        print("  如需重新計算，請將 FORCE_RERUN 改為 True")
        print("[Step 3] 跳過！\n")
        return output_path

    print("\n[Step 3] 開始計算捷運站距離...")

    shops = pd.read_csv(shops_csv)
    mrt = pd.read_csv(MRT_INPUT, encoding="cp950")

    distances, nearest_stations = [], []

    for _, shop in shops.iterrows():
        min_dist = float("inf")
        nearest = ""
        for _, station in mrt.iterrows():
            d = haversine(shop["lat"], shop["lng"], station["緯度"], station["經度"])
            if d < min_dist:
                min_dist = d
                nearest = station["出入口名稱"]
        distances.append(round(min_dist))
        nearest_stations.append(nearest)

    shops["dist_to_mrt"] = distances
    shops["nearest_mrt"] = nearest_stations
    shops["mrt_proximity"] = shops["dist_to_mrt"].apply(proximity_label)

    shops.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"  輸出完成：db2_coffee_shops_with_mrt.csv（{len(shops)} 間）")
    print("[Step 3] 完成！")
    return output_path
