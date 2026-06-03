import os
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.io as pio
from flask import Flask, render_template_string
from datetime import datetime, timedelta

app = Flask(__name__)

# 使用快取檔案路徑，解決 Vercel 頻繁請求的問題
CACHE_FILE = "/tmp/stock_data.csv"
CACHE_EXPIRY_HOURS = 1

def get_data(ticker):
    # 簡單的快取機制：如果 1 小時內抓過資料，就讀取暫存檔
    if os.path.exists(CACHE_FILE):
        file_time = os.path.getmtime(CACHE_FILE)
        if datetime.now() - datetime.fromtimestamp(file_time) < timedelta(hours=CACHE_EXPIRY_HOURS):
            return pd.read_csv(CACHE_FILE, index_col=0, parse_dates=True)

    # 抓取資料
    df = yf.download(ticker, period="1mo", interval="1d", progress=False)
    if not df.empty:
        df.to_csv(CACHE_FILE)
    return df

def get_kline_chart(ticker, title):
    df = get_data(ticker)
    
    if df.empty:
        return f"<p>無法取得 {ticker} 資料，請稍後再試。</p>"
    
    # 建立 K 線圖
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']
    )])
    
    fig.update_layout(title=title, xaxis_rangeslider_visible=False, height=400)
    return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>台股儀表板</title>
    <style>
        body { font-family: sans-serif; padding: 20px; background: #f9f9f9; }
        .container { max-width: 900px; margin: auto; }
        .chart-box { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="container">
        <h1>台股即時分析</h1>
        <div class="chart-box">{{ index_chart | safe }}</div>
        <div class="chart-box">{{ tsmc_chart | safe }}</div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    index_chart = get_kline_chart("^TWII", "台股大盤走勢")
    tsmc_chart = get_kline_chart("2330.TW", "台積電走勢")
    return render_template_string(HTML_TEMPLATE, index_chart=index_chart, tsmc_chart=tsmc_chart)

if __name__ == '__main__':
    app.run(debug=True)