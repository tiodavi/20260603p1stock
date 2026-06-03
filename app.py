import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.io as pio
from flask import Flask, render_template_string, request
from datetime import datetime, timedelta

app = Flask(__name__)

def get_data(ticker, start_date, end_date):
    # 使用 yfinance 抓取區間資料
    df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def get_dashboard_data(ticker):
    # 抓取最近兩日的資料來計算漲跌
    df = yf.download(ticker, period="2d", progress=False, auto_adjust=True)
    if df.empty: return None
    
    curr = df['Close'].iloc[-1]
    prev = df['Close'].iloc[-2]
    change = curr - prev
    pct = (change / prev) * 100
    return {"price": f"{curr:.2f}", "change": f"{change:+.2f}", "pct": f"{pct:+.2f}%", "color": "green" if change >= 0 else "red"}

def get_kline_chart(ticker, title, start_date, end_date):
    df = get_data(ticker, start_date, end_date)
    if df.empty: return f"<p>無 {title} 資料</p>"
    
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(title=title, xaxis_rangeslider_visible=False, height=400)
    return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>台股分析看板</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; padding: 20px; background: #f4f4f9; }
        .container { max-width: 900px; margin: auto; }
        .dashboard { display: flex; gap: 20px; margin-bottom: 20px; }
        .card { background: white; padding: 20px; border-radius: 10px; flex: 1; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; }
        .price { font-size: 24px; font-weight: bold; }
        .up { color: green; } .down { color: red; }
        .controls { background: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>台股即時分析看板</h1>
        
        <div class="dashboard">
            <div class="card">
                <h3>台股大盤 (^TWII)</h3>
                <div class="price">{{ index_data.price }}</div>
                <div class="{{ index_data.color }}">{{ index_data.change }} ({{ index_data.pct }})</div>
            </div>
            <div class="card">
                <h3>台積電 (2330.TW)</h3>
                <div class="price">{{ tsmc_data.price }}</div>
                <div class="{{ tsmc_data.color }}">{{ tsmc_data.change }} ({{ tsmc_data.pct }})</div>
            </div>
        </div>

        <div class="controls">
            <form action="/" method="GET">
                開始日期: <input type="date" name="start" value="{{ start }}">
                結束日期: <input type="date" name="end" value="{{ end }}">
                <button type="submit">更新圖表</button>
            </form>
        </div>
        
        <div class="chart-box">{{ index_chart | safe }}</div>
        <div class="chart-box">{{ tsmc_chart | safe }}</div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    end_date = request.args.get('end', datetime.now().strftime('%Y-%m-%d'))
    start_date = request.args.get('start', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    
    # 獲取看板數據與圖表
    index_data = get_dashboard_data("^TWII")
    tsmc_data = get_dashboard_data("2330.TW")
    index_chart = get_kline_chart("^TWII", "大盤技術線圖", start_date, end_date)
    tsmc_chart = get_kline_chart("2330.TW", "台積電技術線圖", start_date, end_date)
    
    return render_template_string(HTML_TEMPLATE, index_data=index_data, tsmc_data=tsmc_data, 
                                  index_chart=index_chart, tsmc_chart=tsmc_chart, 
                                  start=start_date, end=end_date)

if __name__ == '__main__':
    app.run(debug=True)