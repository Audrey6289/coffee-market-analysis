import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# 【可修改區域】
# ============================================================

# ⚡ 省錢開關（此腳本不耗 API 額度，但可控制是否重新爬取）
FORCE_RERUN = False

# 爬取頁數（每頁約20篇文章，建議5-10頁）
MAX_PAGES = 8

# 體驗關鍵字清單（對應 Dashboard 2 橫條圖）
EXPERIENCE_KEYWORDS = [
    "不限時", "插座", "特色甜點", "寵物友善", "手沖選豆",
    "安靜工作", "Wi-Fi稳定", "停車方便", "外帶",
    "親子友善", "預約制", "自家烘焙", "單品咖啡", "拉花",
]

# ============================================================
# 以下不需要修改
# ============================================================

PTT_BASE = "https://www.ptt.cc"
COFFEE_SEARCH = "https://www.ptt.cc/bbs/Coffee/search?q=體驗"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Cookie": "over18=1"  # PTT 18歲確認
}

def get_article_links(max_pages=5):
    """取得 PTT Coffee 板文章連結"""
    links = []
    url = "https://www.ptt.cc/bbs/Food/search?q=咖啡"

    for page in range(max_pages):
        print(f"  爬取第 {page+1} 頁...")
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")

            # 取得文章連結
            articles = soup.select("div.r-ent div.title a")
            for a in articles:
                href = a.get("href", "")
                if href:
                    links.append(PTT_BASE + href)

            # 找上一頁
            prev = soup.select_one("a.btn.wide:-soup-contains('上頁')")
            if prev:
                url = PTT_BASE + prev["href"]
            else:
                break

            time.sleep(0.5)
        except Exception as e:
            print(f"  錯誤：{e}")
            break

    print(f"  共取得 {len(links)} 篇文章連結")
    return links

def get_article_text(url):
    """取得文章內容"""
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        content = soup.select_one("div#main-content")
        if content:
            return content.get_text()
        return ""
    except:
        return ""

def count_keywords(texts, keywords):
    """計算關鍵字出現頻率"""
    results = []
    total_articles = len(texts)

    for keyword in keywords:
        count = sum(1 for text in texts if keyword in text)
        pct = round(count / total_articles * 100) if total_articles > 0 else 0
        results.append({
            "keyword": keyword,
            "frequency_pct": pct,
            "category": "體驗因素"
        })

    results.sort(key=lambda x: -x["frequency_pct"])
    return results

def run_ptt(output_dir=None):
    """爬取 PTT Coffee 板，產出 db2_experience_real.csv"""
    if output_dir is None:
        output_dir = os.path.join(HERE, "output")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "db2_experience_real.csv")

    # ⚡ 省錢檢查
    if not FORCE_RERUN and os.path.exists(output_path):
        print("\n[Step 6] 偵測到現有資料，跳過爬蟲（省錢模式）")
        print(f"  使用現有檔案：{output_path}")
        print("  如需重新爬取，請將 FORCE_RERUN 改為 True")
        print("[Step 6] 跳過！\n")
        return output_path

    print("\n[Step 6] 開始爬取 PTT Coffee 板...")

    # 取得文章連結
    links = get_article_links(max_pages=MAX_PAGES)

    # 取得文章內容
    print(f"\n  開始讀取 {len(links)} 篇文章內容...")
    texts = []
    for i, link in enumerate(links):
        if i % 10 == 0:
            print(f"  進度：{i}/{len(links)}")
        text = get_article_text(link)
        if text:
            texts.append(text)
        time.sleep(0.3)

    print(f"  成功取得 {len(texts)} 篇文章")

    # 計算關鍵字頻率
    results = count_keywords(texts, EXPERIENCE_KEYWORDS)

    # 輸出 CSV
    df = pd.DataFrame(results)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\n  輸出完成：db2_experience_real.csv（{len(df)} 筆）")
    print("\n  關鍵字頻率：")
    for r in results:
        bar = "█" * (r["frequency_pct"] // 5)
        print(f"  {r['keyword']:<10} {r['frequency_pct']:>3}%  {bar}")
    print("[Step 6] 完成！")
    return output_path

if __name__ == "__main__":
    run_ptt()
