
# 粉塵監控告警系統

本專案是一套粉塵監控與告警系統，實現粉塵數據的自動化收集、分析、展示與告警功能，適用於工業場景的粉塵監測需求。

---

## 專案結構

```plaintext
├── app.py                  # 主程式，使用 Streamlit 作為前端介面
├── sqlite.py               # 資料庫監控與管理工具
├── data_emulator.py        # 模擬粉塵數據生成器
├── config.yaml             # 系統配置文件
├── data/                   # 儲存模擬生成的粉塵數據 CSV 文件
├── requirements.txt        # Python 套件需求
└── dust_data.db            # SQLite 資料庫文件
```

---

## 功能特性

1. **實時粉塵數據監控**
   - 利用 Streamlit 實現數據展示，包括圓餅圖與折線圖。
   - 提供粉塵隨時間變化的趨勢分析。

2. **告警值調整**
   - 支援動態調整黃色與紅色警戒值。

3. **數據管理**
   - 自動監控資料夾內新增的粉塵數據文件並匯入 SQLite 資料庫。
   - 自動清理舊的 CSV 文件，僅保留最新 10 筆。

4. **數據模擬**
   - 提供粉塵數據模擬器，模擬工廠環境中的粉塵水平。

---

## 安裝步驟

1. 安裝 Python 環境（版本 3.8 或以上）。
2. 使用以下命令安裝必要套件：
   ```bash
   pip install -r requirements.txt
   ```

---

## 使用方法

### 啟動數據模擬器

在終端執行以下命令以模擬粉塵數據：
```bash
python data_emulator.py
```

### 啟動監控程式

在另一個終端執行以下命令以啟動數據監控系統：
```bash
python sqlite.py
```

### 啟動前端介面

在另一個終端執行以下命令啟動 Web 介面：
```bash
streamlit run app.py
```

前端介面將運行於 [http://localhost:8501](http://localhost:8501)。

---

## 配置說明

### config.yaml

- `rtsp_url`: 用於後續擴展 RTSP 視訊串流的 URL（目前未啟用）。
- `refresh_interval`: 頁面刷新間隔時間（秒）。
- `thresholds.yellow_line`: 黃色警戒值，默認為 45。
- `thresholds.red_line`: 紅色警戒值，默認為 60。

---

## 系統需求

- Python 3.8 或以上
- SQLite 資料庫

---

## 注意事項

1. 模擬器每 10 秒生成一筆粉塵數據，請確認 `data/` 資料夾有讀寫權限。
2. 請確保 `dust_data.db` 資料庫文件在程式目錄下，如無則系統會自動生成。
3. 若需更改資料匯入行為，請調整 `sqlite.py` 中的相關邏輯。

---

如果需要更詳細的內容或進一步問題，請隨時告知！
