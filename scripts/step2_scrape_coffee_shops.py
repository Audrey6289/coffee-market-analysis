import requests
import pandas as pd
import time
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# 【可修改區域】
# ============================================================
API_KEY = "YOUR_GOOGLE_MAPS_API_KEY"

# ⚡ 省錢開關：False = 有舊資料就直接用，不重新爬（節省 API 額度）
#              True  = 強制重新爬取最新資料
FORCE_RESCRAPE = False

DISTRICTS = [
    {"name": "中正區", "lat": 25.0320, "lng": 121.5196},
    {"name": "大同區", "lat": 25.0630, "lng": 121.5130},
    {"name": "中山區", "lat": 25.0631, "lng": 121.5398},
    {"name": "松山區", "lat": 25.0579, "lng": 121.5773},
    {"name": "大安區", "lat": 25.0267, "lng": 121.5435},
    {"name": "萬華區", "lat": 25.0340, "lng": 121.4997},
    {"name": "信義區", "lat": 25.0330, "lng": 121.5654},
    {"name": "士林區", "lat": 25.0934, "lng": 121.5261},
    {"name": "北投區", "lat": 25.1316, "lng": 121.5019},
    {"name": "內湖區", "lat": 25.0832, "lng": 121.5873},
    {"name": "南港區", "lat": 25.0549, "lng": 121.6071},
    {"name": "文山區", "lat": 24.9988, "lng": 121.5706},
]

SEARCH_RADIUS = 1500
CHAIN_KEYWORDS = ["星巴克", "STARBUCKS", "路易莎", "cama", "伯朗", "丹堤", "西雅圖", "客美多", "湛盧"]

# ============================================================
# 以下不需要修改
# ============================================================

def classify_brand(shop_name):
    for keyword in CHAIN_KEYWORDS:
        if keyword.lower() in shop_name.lower():
            return "連鎖"
    return "獨立"

def nearby_search(lat, lng, radius=1500):
    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "places.id,places.displayName,places.location,places.rating,places.userRatingCount,places.formattedAddress"
    }
    body = {
        "includedTypes": ["cafe"],
        "maxResultCount": 20,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": radius
            }
        }
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        return response.json().get("places", [])
    else:
        print(f"  錯誤：{response.status_code} - {response.text}")
        return []

def run_scrape(output_dir=None):
    """爬取台北市各行政區咖啡廳，產出 coffee_shops_real.csv"""
    if output_dir is None:
        output_dir = os.path.join(HERE, "output")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "coffee_shops_real.csv")

    # ⚡ 省錢檢查：有舊資料且未強制重爬 → 直接跳過
    if not FORCE_RESCRAPE and os.path.exists(output_path):
        print("\n[Step 2] 偵測到現有資料，跳過爬蟲（省錢模式）")
        print(f"  使用現有檔案：{output_path}")
        print("  如需重新爬取，請將 FORCE_RESCRAPE 改為 True")
        print("[Step 2] 跳過！\n")
        return output_path

    print("\n[Step 2] 開始爬取 Google Maps 咖啡廳資料...")
    all_shops = []
    seen_ids = set()

    for district in DISTRICTS:
        print(f"  搜尋中：{district['name']}...")
        places = nearby_search(district["lat"], district["lng"], SEARCH_RADIUS)

        for place in places:
            place_id = place.get("id", "")
            if place_id in seen_ids:
                continue
            seen_ids.add(place_id)

            name = place.get("displayName", {}).get("text", "")
            shop = {
                "shop_name": name,
                "address": place.get("formattedAddress", ""),
                "district": district["name"],
                "lat": place.get("location", {}).get("latitude", ""),
                "lng": place.get("location", {}).get("longitude", ""),
                "rating": place.get("rating", ""),
                "review_count": place.get("userRatingCount", ""),
                "brand_type": classify_brand(name),
            }
            all_shops.append(shop)

        print(f"    → 找到 {len(places)} 間（累計 {len(all_shops)} 間）")
        time.sleep(0.5)

    df = pd.DataFrame(all_shops)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"  輸出完成：coffee_shops_real.csv（{len(df)} 間）")
    print("[Step 2] 完成！")
    return output_path
