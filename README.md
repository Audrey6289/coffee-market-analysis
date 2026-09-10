# 台灣咖啡市場趨勢與展店策略分析

`Python` · `Power BI` · `Google Maps API` · `Kaggle`

---

## 專案背景

開一間咖啡廳的成本很高，不能只靠直覺選地點或定價。這份專案的出發點很簡單：用數據幫一個想進入台灣精品咖啡市場的新品牌，回答三個最核心的決策問題。

- 現在進場時機對嗎？市場還在長大嗎？
- 店要開在哪裡？飲品要賣多少錢？
- 賣什麼組合最賺？怎麼做促銷才能養出回頭客？

---

## 資料來源

| 資料 | 來源 | 取得方式 |
|------|------|---------|
| 咖啡豆進出口統計 | 財政部關務署 | 下載 CSV |
| 全台咖啡館家數與銷售額 | 財政部統計年報 | 下載 CSV |
| 品牌市占率 | 未來流通研究所 2023 | 公開數據引用 |
| 雙北咖啡廳評分、評論、座標 | Google Maps Places API | Python 爬蟲 |
| 捷運站出入口座標 | 政府開放資料平台 | 下載 CSV |
| 競品菜單定價 | 各大連鎖品牌官網 | Python 爬蟲 |
| 消費者選店關鍵字 | PTT Food 板、Google 評論 | Python 爬蟲 + jieba 斷詞 |
| 咖啡廳交易明細 | Kaggle（Coffee Shop Sales） | 下載 CSV |

---

## 分析流程

```
原始資料收集
（API 串接 / 爬蟲 / 政府下載）
        ↓
Python 資料清洗與整合
（欄位標準化、中文化、距離計算、關聯規則、Cohort 留存）
        ↓
Power BI 互動式儀表板
（三張 Dashboard，對應三個決策層級）
```

---

## 儀表板說明

### Dashboard 1｜市場大局 × 競品感知
> 給想評估「要不要進這個市場」的決策者看

- 台灣咖啡進口趨勢折線圖（含 2027 年預測）
- 精品豆 vs 商業豆進口比例消長
- 各大品牌市占率環形圖
- 連鎖品牌 vs 精品獨立店 Google 評論文字雲對比

### Dashboard 2｜黃金選址 × 體驗定價
> 給負責找店面、定售價的展店團隊看

- 雙北咖啡廳密度地圖（泡泡大小=人潮，顏色=距捷運遠近）
- 消費者選店關鍵因素橫條圖
- 各大連鎖品牌定價比較（美式 vs 拿鐵）

### Dashboard 3｜商品策略 × 行銷成效
> 給決定賣什麼、怎麼促銷的行銷與採購主管看

- 精品豆 vs 商業豆毛利貢獻比較
- 價格彈性散佈圖（漲價對銷量的影響）
- 飲品 × 點心同購率關聯矩陣（Kaggle 資料集）
- 行銷活動世代留存熱力圖（Cohort Analysis）

<img width="611" height="341" alt="image" src="https://github.com/user-attachments/assets/c6c5d44f-4567-46f9-8460-7f9608fb1bc6" />

<img width="602" height="341" alt="image" src="https://github.com/user-attachments/assets/ad9046df-1a53-42dd-93f9-a2ef12142110" />

<img width="607" height="343" alt="image" src="https://github.com/user-attachments/assets/c1ac50da-f3d4-4e69-a19e-58bed4998aa0" />
---

## 使用工具

- **Python**：BeautifulSoup、pandas、jieba
- **Power BI**：DAX、DirectQuery、條件格式化、互動式篩選器
- **Google Maps Places API**：店家資料、評論爬取

---

## 資料夾結構

```
├── main.py                          # 執行入口
├── step1_clean.py                   # 政府資料清洗
├── step2_scrape_coffee_shops.py     # Google Maps 爬蟲
├── step3_calculate_mrt_distance.py  # 捷運距離計算
├── step4_pricing.py                 # 競品定價爬蟲
├── step5_wordcloud.py               # 評論文字雲
├── step6_ptt.py                     # PTT 關鍵字萃取
├── step7_merge_experience.py        # 體驗關鍵字整合
├── step8_etl_coffee_kaggle.py       # Kaggle 資料 ETL
├── output/                          # Power BI 資料來源（清洗後 CSV）
└── coffee_BI.pbix                   # Power BI 報告檔
```

---

## 備註

- Dashboard 3 的關聯矩陣使用 Kaggle 交易資料計算
- Cohort 留存圖因 Kaggle 資料集僅含單月交易記錄，以模擬示意數據呈現，圖表內已標注
- 品牌市占率引用未來流通研究所公開數據，其餘為推估值，圖表旁已標注來源
