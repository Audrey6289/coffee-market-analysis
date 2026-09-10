import csv
import os
import re
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))

SPECIALTY_COUNTRIES = {
    "衣索比亞", "哥倫比亞", "巴拿馬", "肯亞", "盧安達", "蒲隆地",
    "葉門", "牙買加", "巴西", "瓜地馬拉", "宏都拉斯", "哥斯大黎加",
    "尼加拉瓜", "薩爾瓦多", "秘魯", "玻利維亞", "坦尚尼亞", "烏干達",
    "馬達加斯加", "喀麥隆", "剛果", "剛果民主共和國", "印尼", "越南",
    "東帝汶", "巴布亞紐幾內亞", "印度", "寮國", "泰國", "緬甸",
    "尼泊爾", "多明尼加", "海地", "墨西哥", "古巴", "厄瓜多",
    "留尼旺", "馬拉威", "尚比亞", "多米尼克",
}

def classify_country(country):
    return "精品豆" if country in SPECIALTY_COUNTRIES else "商業豆"

def parse_year(text):
    m = re.search(r"(\d+)", text)
    return int(m.group(1)) + 1911 if m else 0

def save_csv(output_dir, filename, rows):
    path = os.path.join(output_dir, filename)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  輸出完成：{filename}（{len(rows)} 筆）")

def run(sh_path=None, su_path=None, output_dir=None):
    sh_path = sh_path or os.path.join(HERE, "生豆.csv")
    su_path = su_path or os.path.join(HERE, "熟豆.csv")
    output_dir = output_dir or os.path.join(HERE, "output")
    os.makedirs(output_dir, exist_ok=True)

    for path, name in [(sh_path, "生豆.csv"), (su_path, "熟豆.csv")]:
        if not os.path.exists(path):
            print(f"找不到 {name}，請確認路徑：{path}")
            return

    print("【Step 1】清洗進口資料...")
    all_rows = []
    for filepath, bean_label in [(sh_path, "生豆"), (su_path, "烘焙熟豆")]:
        raw = open(filepath, "rb").read()
        text = raw.decode("big5", errors="replace")
        for row in csv.DictReader(text.splitlines()):
            if row.get("進出口別", "").strip() != "進口":
                continue
            year = parse_year(row.get("日期", ""))
            country = row.get("國家", "").strip()
            value = row.get("美元(千元)", "0").replace(",", "").strip()
            if year == 0:
                continue
            all_rows.append({
                "year": year,
                "country": country,
                "bean_type": bean_label,
                "specialty": classify_country(country),
                "value_kUSD": float(value or 0),
            })

    print(f"  讀取完成，共 {len(all_rows)} 筆進口記錄")

    yearly = defaultdict(lambda: {"total": 0, "specialty": 0, "commercial": 0, "roasted": 0})
    for r in all_rows:
        y = r["year"]
        yearly[y]["total"] += r["value_kUSD"]
        yearly[y]["roasted"] += r["value_kUSD"] if r["bean_type"] == "烘焙熟豆" else 0
        if r["specialty"] == "精品豆":
            yearly[y]["specialty"] += r["value_kUSD"]
        else:
            yearly[y]["commercial"] += r["value_kUSD"]

    years = sorted(yearly.keys())
    trend = []
    for i, y in enumerate(years):
        d = yearly[y]
        tot = d["total"]
        prev = yearly[years[i - 1]]["total"] if i > 0 else None
        yoy = round((tot / prev - 1) * 100, 1) if prev else None
        trend.append({
            "year": y,
            "total_kUSD": round(tot),
            "specialty_kUSD": round(d["specialty"]),
            "commercial_kUSD": round(d["commercial"]),
            "roasted_kUSD": round(d["roasted"]),
            "specialty_pct": round(d["specialty"] / tot * 100, 1) if tot else 0,
            "roasted_pct": round(d["roasted"] / tot * 100, 1) if tot else 0,
            "yoy_pct": yoy,
            "is_forecast": 0,
        })

    recent_yoy = [r["yoy_pct"] for r in trend[-3:] if r["yoy_pct"]]
    avg_growth = sum(recent_yoy) / len(recent_yoy) / 100 if recent_yoy else 0.05
    last_total = trend[-1]["total_kUSD"]
    last_spec = trend[-1]["specialty_pct"]
    last_year = trend[-1]["year"]

    for offset in [1, 2]:
        proj_total = round(last_total * (1 + avg_growth) ** offset)
        proj_spec = min(round(last_spec + 1.5 * offset, 1), 95)
        trend.append({
            "year": last_year + offset,
            "total_kUSD": proj_total,
            "specialty_kUSD": round(proj_total * proj_spec / 100),
            "commercial_kUSD": round(proj_total * (100 - proj_spec) / 100),
            "roasted_kUSD": round(proj_total * proj_spec / 100),
            "specialty_pct": proj_spec,
            "roasted_pct": proj_spec,
            "yoy_pct": round(avg_growth * 100, 1),
            "is_forecast": 1,
        })

    country_totals = defaultdict(lambda: {"total": 0, "specialty": ""})
    for r in all_rows:
        country_totals[r["country"]]["total"] += r["value_kUSD"]
        country_totals[r["country"]]["specialty"] = r["specialty"]

    country_rows = [
        {"country": k, "specialty": v["specialty"], "total_kUSD": round(v["total"])}
        for k, v in country_totals.items()
    ]
    country_rows.sort(key=lambda x: -x["total_kUSD"])
    for i, r in enumerate(country_rows):
        r["rank"] = i + 1

    save_csv(output_dir, "db1_yearly_trend.csv", trend)
    save_csv(output_dir, "db1_country_rank.csv", country_rows)
    print("【Step 1】完成！\n")