import sqlite3
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import yaml


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
    st.success("成功從資料庫讀取資料！")
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
else:
    st.warning("資料庫中沒有資料！")

# 自定義樣式
st.markdown(
    """
    <style>
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
red_line = st.sidebar.slider("紅色警戒值", 0, 100, default_red_line)

# 警戒計算
yellow_alerts = (df["Dust_Level"] > yellow_line).sum()
red_alerts = (df["Dust_Level"] > red_line).sum()
safe_alerts = len(df) - yellow_alerts

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
