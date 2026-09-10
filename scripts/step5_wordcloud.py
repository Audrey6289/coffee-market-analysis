import requests
import jieba
import pandas as pd
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# 【可修改區域】
# ============================================================
API_KEY = "YOUR_GOOGLE_MAPS_API_KEY"

# ⚡ 省錢開關：False = 有舊資料就直接用
#              True  = 強制重新爬取評論
FORCE_RERUN = False

# 要分析的品牌與對應的 Place ID
BRANDS = {
    "連鎖品牌": [
        {"name": "星巴克 永和頂溪門市","place_id": "ChIJ48nCrsKpQjQRE4qA5mSx-64"},
        {"name": "路易莎咖啡 板橋文化門市","place_id": "ChIJbXwSrBeoQjQRsGIkgDiyea8"},
        {"name": "cama café 新店中正店","place_id": "ChIJqbnvIDoDaDQRNFFERGDu5eY"},
    ],
    "精品獨立": [
        {"name": "Rebirth cafe心，聚點","place_id": "ChIJYcxTMAuqQjQR3bv9q3Fsphs"},
        {"name": "在山野對話","place_id": "ChIJh4TtY2OsQjQRCp84j2uCCzo"},
        {"name": "隅咖啡Aroundtheblock","place_id": "ChIJU5sK7vypQjQRxC00sY0q-80"},
    ]
}

# 停用詞（不計入詞頻）
STOP_WORDS = {
    # 基本虛詞
    "的", "了", "是", "在", "我", "有", "和", "就", "都", "而", "及", "與",
    "著", "或", "一", "也", "這", "那", "你", "他", "她", "它", "們",
    "很", "非常", "真的", "還", "但", "但是", "不", "沒", "沒有", "一個",
    "可以", "因為", "所以", "如果", "雖然", "然後", "這裡", "這個", "一樣",
    "讓", "把", "被", "將", "對", "從", "到", "向", "跟", "與", "及",
    "啊", "吧", "呢", "嗎", "喔", "唉", "哦", "嗯", "哈", "呵",

    # 無分析價值的描述詞
    "看到", "不是", "這樣", "時候", "一位", "隔壁", "完全", "工作", "照片",
    "自己", "或是", "其他", "因此", "雖然", "不過", "而且", "所以", "但是",
    "覺得", "感覺", "感受", "發現", "知道", "認為", "覺得", "應該", "需要",
    "可能", "已經", "還是", "還有", "沒有", "不會", "不太", "不夠", "不錯",
    "一下", "一次", "一直", "一定", "一些", "一起", "一般", "一共", "一樣",
    "真的", "確實", "其實", "畢竟", "反正", "總之", "總是", "總共",
    "然後", "接著", "再來", "最後", "最近", "最好", "最多", "最少",
    "比較", "相比", "相當", "相同", "不同", "有點", "有些", "有時",
    "每次", "每個", "每天", "每種", "整個", "整體", "整體來說",
    "進來", "出去", "回來", "過來", "上來", "下去", "進去",

    # 時間詞
    "今天", "昨天", "明天", "上次", "這次", "那次", "以前", "之前", "之後",
    "最近", "現在", "當時", "那時", "平時", "平常", "偶爾", "經常", "一直",

    # 數量詞
    "一些", "很多", "不少", "許多", "幾個", "幾次", "幾乎", "大概", "大約",
    "左右", "以上", "以下", "以內", "超過",

    # 方向/位置詞
    "旁邊", "附近", "隔壁", "對面", "裡面", "外面", "上面", "下面", "前面", "後面",
    "這裡", "那裡", "哪裡", "地方", "位置", "區域",

    # 品牌名稱（不算分析關鍵字）
    "星巴克", "路易莎", "cama", "starbucks", "louisa",
    "咖啡", "咖啡廳", "咖啡店", "門市", "分店", "店家", "店裡", "店內",

    # 動詞（無特定分析意義）
    "來", "去", "到", "說", "喝", "點", "買", "吃", "會", "要", "想",
    "看", "找", "用", "做", "給", "拿", "坐", "站", "走", "進", "出",
    "試", "等", "問", "回", "開", "關", "放", "帶", "推", "拉",
    "覺得", "感覺", "看到", "聽到", "知道", "告訴", "提到", "說到",

    # 代名詞
    "我們", "你們", "他們", "她們", "它們", "大家", "自己", "別人",
    
    # 跑後新增
    "什麼", "只要", "不行", "一開始", "適合", "文山", "蘋果",
    "客人", "位子", "櫃子", "大聲", "認真", "點餐", "生活",
    "一些", "這些", "那些", "這種", "那種", "如何", "怎麼",
    "好像", "感覺", "似乎", "應該", "可能", "大概", "左右",
    '第一次','這位','值班','今晚','首先','二樓','中清潔','一口',

    # 英文停用詞
    "the", "and", "is", "to", "of", "it", "with", "was", "my", "for",
    "very", "a", "an", "in", "at", "on", "this", "that", "i", "we",
    "are", "be", "been", "but", "have", "had", "not", "they", "he",
    "she", "so", "if", "as", "by", "do", "did", "get", "got", "here",
    "its", "no", "or", "our", "out", "up", "what", "when", "which",
    "who", "will", "would", "you", "your", "there", "their", "from",
    "one", "all", "were", "like", "how", "them", "best", "nice",
    "good", "great", "shop", "time", "can", "also", "some", "The",
    "It", "This", "I", "A", "In", "At", "coffee", "place", "There",
}

# ============================================================
# 爬蟲函式
# ============================================================

def get_reviews(place_id):
    """用 Places API (New) 抓取評論"""
    url = f"https://places.googleapis.com/v1/places/{place_id}"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "reviews"
    }
    params = {"languageCode": "zh-TW"}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        reviews = data.get("reviews", [])
        texts = []
        for r in reviews:
            text = r.get("text", {}).get("text", "")
            if text:
                texts.append(text)
        return texts
    else:
        print(f"  錯誤：{response.status_code} - {response.text}")
        return []

def extract_keywords(texts, top_n=15):
    """用 jieba 斷詞並計算詞頻"""
    all_words = []
    for text in texts:
        words = jieba.cut(text)
        for word in words:
            word = word.strip()
            if len(word) >= 2 and word not in STOP_WORDS:
                all_words.append(word)
    counter = Counter(all_words)
    return counter.most_common(top_n)

# ============================================================
# 主函式
# ============================================================

def run_wordcloud(output_dir=None):
    """爬取評論並產出 db1_wordcloud.csv"""
    if output_dir is None:
        output_dir = os.path.join(HERE, "output")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "db1_wordcloud.csv")

    # ⚡ 省錢檢查
    if not FORCE_RERUN and os.path.exists(output_path):
        print("\n[Step 5] 偵測到現有資料，跳過爬蟲（省錢模式）")
        print(f"  使用現有檔案：{output_path}")
        print("  如需重新爬取，請將 FORCE_RERUN 改為 True")
        print("[Step 5] 跳過！\n")
        return output_path

    print("\n[Step 5] 開始爬取 Google 評論並分析關鍵字...")

    results = []

    for brand_type, shops in BRANDS.items():
        print(f"\n  品牌類型：{brand_type}")
        all_texts = []

        for shop in shops:
            print(f"    抓取：{shop['name']}...")
            texts = get_reviews(shop["place_id"])
            print(f"      → 取得 {len(texts)} 則評論")
            all_texts.extend(texts)

        keywords = extract_keywords(all_texts, top_n=15)
        print(f"  top 15 關鍵字：{[k for k, v in keywords]}")

        for keyword, frequency in keywords:
            results.append({
                "keyword": keyword,
                "frequency": frequency,
                "brand_type": brand_type,
                "sentiment": "正面"
            })

    df = pd.DataFrame(results)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\n  輸出完成：db1_wordcloud.csv（{len(df)} 筆）")
    print("[Step 5] 完成！")
    return output_path

if __name__ == "__main__":
    run_wordcloud()