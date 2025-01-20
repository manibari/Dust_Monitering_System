import sqlite3
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import yaml
import subprocess
import os


# 讀取 YAML 配置文件
def load_config(config_path="config.yaml"):
    """讀取配置文件"""
    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    return config


# HTML 自動刷新加載配置
config = load_config()
refresh_interval = config["settings"]["refresh_interval"]

# HTML 自動刷新 (每 10 秒刷新一次)
st.markdown(
    """
    <meta http-equiv="refresh" content="{refresh_interval}">
    """,
    unsafe_allow_html=True
)


# 連接 SQLite 資料庫並取得資料

def load_data_from_sqlite(db_path="dust_data.db", table_name="dust_data"):
    """從 SQLite 資料庫讀取資料"""
    try:
        conn = sqlite3.connect(db_path)
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"無法讀取資料庫: {e}")
        return pd.DataFrame({"Timestamp": [], "Dust_Level": []})


# 載入資料
df = load_data_from_sqlite()
if not df.empty:
    # st.success("成功從資料庫讀取資料！")
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
else:
    st.warning("資料庫中沒有資料！")



# 自定義樣式
st.markdown(
    """
    <style>
    .main .block-container {
        max-width: 2000px; /* 設置內容最大寬度 */
        padding: 1rem;     /* 調整內容左右內距 */
    }
    .custom-block {
        background-color: #f0f0f0;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .custom-title {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 頁面標題
st.title("粉塵監控告警介面")
st.subheader("產線：碼槽 BC6 硫磺產線")


# 初始化警戒值
config = load_config()
default_yellow_line = config["thresholds"]["yellow_line"]
default_red_line = config["thresholds"]["red_line"]

# 調整警戒值
st.sidebar.header("調整警戒值")
yellow_line = st.sidebar.slider("黃色警戒值", 0, 100, default_yellow_line)
red_line = st.sidebar.slider("紅色警戒值", yellow_line, 100, default_red_line)

# 警戒計算
yellow_alerts = (df["Dust_Level"] > yellow_line).sum()
red_alerts = (df["Dust_Level"] > red_line).sum()
safe_alerts = len(df) - yellow_alerts

# 初始化 Session State
if "page" not in st.session_state:
    st.session_state.page = "調整設定"  # 預設頁面為 "調整設定"


# Sidebar 功能選單
with st.sidebar:
    st.header("功能選單")
    if st.button("調整設定"):
        st.session_state.page = "調整設定"

    if st.button("歷史資料"):
        st.session_state.page = "歷史資料"






# 第零個區塊：即時紅綠燈顯示
st.markdown('<div class="custom-block">', unsafe_allow_html=True)
st.markdown('<div class="custom-title">即時粉塵狀態</div>', unsafe_allow_html=True)

if not df.empty:
    # 獲取最新的粉塵數據
    latest_dust_level = df["Dust_Level"].iloc[-1]

    # 確定當前狀態
    if latest_dust_level > red_line:
        current_status = "危險"
        color = "red"
    elif latest_dust_level > yellow_line:
        current_status = "警告"
        color = "orange"
    else:
        current_status = "安全"
        color = "green"

    # 顯示紅綠燈
    st.markdown(
        f"""
        <style>
        .status-indicator {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 75px;
            background-color: {color};
            color: white;
            font-size: 22px;
            font-weight: bold;
            border-radius: 8px;
        }}
        </style>
        <div class="status-indicator">
            {current_status}
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.warning("目前無法顯示即時狀態，因為資料庫中沒有數據！")

st.markdown('</div>', unsafe_allow_html=True)

# 第一個區塊：圓餅圖與表格
st.markdown('<div class="custom-block">', unsafe_allow_html=True)
st.markdown('<div class="custom-title">本日粉塵安全度總覽</div>',
            unsafe_allow_html=True)

# 圓餅圖
col1, col2 = st.columns(2)

with col1:
    # 設定圖表大小
    fig = go.Figure(make_subplots(
        rows=1, cols=1, specs=[[{'type': 'domain'}]]
    ))
    fig.add_trace(go.Pie(
        labels=["安全", "警告", "危險"],
        values=[safe_alerts, yellow_alerts - red_alerts, red_alerts],
        hole=.5,
        marker_colors=["green", "orange", "red"]
    ))
    fig.update_traces(hoverinfo='label+percent',
                      textinfo='label', textfont_size=14)
    fig.update_layout(
        width=400,  # 圖表寬度
        height=400  # 圖表高度
    )
    st.plotly_chart(fig, use_container_width=False)  # 禁用自動調整寬度

with col2:
    # 表格內容與樣式
    table_data = pd.DataFrame({
        "狀態": ["危險", "警告", "安全"],
        "觸發次數": [red_alerts, yellow_alerts - red_alerts, safe_alerts]
    })
    st.markdown("""
        <style>
        .custom-table {
            border-collapse: collapse;
            width: 100%;
            height: 400px; /* 與圖表高度對齊 */
            display: flex; /* 使用 flex 布局 */
            justify-content: center; /* 水平居中 */
            align-items: center; /* 垂直居中 */
        }
        .custom-table th, .custom-table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }
        .custom-table th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)
    st.markdown(
        f'<div class="custom-table">{table_data.to_html(index=False)}</div>',
        unsafe_allow_html=True
    )


# 第二個區塊：時間序列圖
st.markdown('<div class="custom-block">', unsafe_allow_html=True)
st.markdown('<div class="custom-title">粉塵隨時間變化</div>', unsafe_allow_html=True)

if not df.empty:
    filtered_df = df.tail(360)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(filtered_df["Timestamp"], filtered_df["Dust_Level"],
            label="Dust Level", linewidth=1)
    ax.axhline(y=yellow_line, color='yellow', linestyle='--',
               label=f'Yellow Warning Line ({yellow_line})')
    ax.axhline(y=red_line, color='red', linestyle='--',
               label=f'Red Warning Line ({red_line})')
    ax.set_title("Dust Level Change for the Last 1 hour", fontsize=14)
    ax.set_xlabel("Time", fontsize=12)
    ax.set_ylabel("Dust Level", fontsize=12)
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45, fontsize=10)
    st.pyplot(fig)

st.markdown('</div>', unsafe_allow_html=True)


# "調整設定"頁面部分
if st.session_state.page == "調整設定":
    st.header("調整設定")

    # 配置文件路徑
    config_path = "config.yaml"

    # 顯示文件編輯按鈕
    if os.path.exists(config_path):
        st.write(f"配置文件路徑：{config_path}")

        # 按下按鈕開啟文件進行編輯
        if st.button("開啟配置文件進行編輯"):
            try:
                # 在默認文本編輯器中打開文件
                subprocess.Popen(["notepad", config_path]
                                 if os.name == "nt" else ["open", config_path])
                st.success("配置文件已打開，請進行編輯！")
            except Exception as e:
                st.error(f"無法打開配置文件: {e}")
    else:
        st.error("配置文件不存在！請確認路徑是否正確。")

# "歷史資料"頁面部分
if st.session_state.page == "歷史資料":
    st.markdown("<div class=\"custom-block\">", unsafe_allow_html=True)
    st.markdown("<div class=\"custom-title\">歷史數據查詢</div>", unsafe_allow_html=True)

    # 使用既有的 load_data_from_sqlite 函數讀取資料庫
    db_path = st.text_input("輸入 SQLite 資料庫路徑", value="dust_data.db")

    if os.path.exists(db_path):
        try:
            # 連接 SQLite 資料庫
            conn = sqlite3.connect(db_path)
            st.success("成功連接資料庫！")

            # 顯示資料表列表
            query = "SELECT name FROM sqlite_master WHERE type='table';"
            tables = pd.read_sql(query, conn)

            if not tables.empty:
                table_name = st.selectbox("選擇資料表", tables["name"])

                # 查詢選定的資料表
                if table_name:
                    query = f"SELECT * FROM {table_name}"
                    data = pd.read_sql(query, conn)

                    if not data.empty:
                        # 確保 Timestamp 欄位正確轉換為 datetime 格式
                        if "Timestamp" in data.columns:
                            data["Timestamp"] = pd.to_datetime(data["Timestamp"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
                            if data["Timestamp"].isna().any():
                                st.warning("部分 Timestamp 資料無法解析，請檢查資料格式！")
                            
                        # 日期篩選
                        col1, col2 = st.columns(2)
                        with col1:
                            start_date = st.date_input("選擇起始日期", value=data["Timestamp"].min().date() if "Timestamp" in data.columns and not data["Timestamp"].isna().all() else None)
                        with col2:
                            end_date = st.date_input("選擇結束日期", value=data["Timestamp"].max().date() if "Timestamp" in data.columns and not data["Timestamp"].isna().all() else None)

                        if "Timestamp" in data.columns and not data["Timestamp"].isna().all():
                            filtered_data = data[(data["Timestamp"] >= pd.Timestamp(start_date)) & (data["Timestamp"] <= pd.Timestamp(end_date)+timedelta(seconds=86400))]
                        else:
                            st.warning("選擇的資料表中不包含有效的 'Timestamp' 欄位，無法進行日期篩選！")
                            filtered_data = data

                        # 顯示篩選後的數據
                        st.dataframe(filtered_data, use_container_width=True)

                        # CSV 文件下載
                        csv = filtered_data.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="下載篩選後的數據為 CSV",
                            data=csv,
                            file_name=f"{table_name}_filtered.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("該資料表中沒有數據！")
                else:
                    st.warning("請選擇一個資料表進行查詢！")
            else:
                st.warning("資料庫中沒有找到資料表！")

            conn.close()
        except Exception as e:
            st.error(f"無法讀取資料庫: {e}")
    else:
        st.warning("指定的資料庫路徑不存在！請確認路徑是否正確。")

    st.markdown("</div>", unsafe_allow_html=True)


