import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.io as pio
from flask import Flask, render_template_string, request
from datetime import datetime, timedelta

app = Flask(__name__)

def get_data(ticker, start_date, end_date):
    # 直接抓取指定區間，不依賴本機快取 (避免日期範圍衝突)
    df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def get_kline_chart(ticker, title, start_date, end_date):
    df = get_data(ticker, start_date, end_date)
    
    if df.empty:
        return f"<p>無 {title} 在 {start_date} 至 {end_date} 之間的資料。</p>"
    
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
    <title>台股日期篩選分析</title>
    <style>
        body { font-family: sans-serif; padding: 20px; background: #f4f4f9; }
        .container { max-width: 900px; margin: auto; }
        .controls { background: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .chart-box { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>台股自訂區間分析</h1>
        <div class="controls">
            <form action="/" method="GET">
                開始日期: <input type="date" name="start" value="{{ start }}">
                結束日期: <input type="date" name="end" value="{{ end }}">
                <button type="submit">查詢</button>
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
    # 獲取 GET 參數，預設為過去 30 天
    end_date = request.args.get('end', datetime.now().strftime('%Y-%m-%d'))
    start_date = request.args.get('start', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    
    index_chart = get_kline_chart("^TWII", "台股大盤走勢", start_date, end_date)
    tsmc_chart = get_kline_chart("2330.TW", "台積電走勢", start_date, end_date)
    
    return render_template_string(HTML_TEMPLATE, index_chart=index_chart, tsmc_chart=tsmc_chart, start=start_date, end=end_date)

if __name__ == '__main__':
    app.run(debug=True)