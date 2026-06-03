import pandas as pd
import requests
import plotly.graph_objects as go
import plotly.io as pio
from flask import Flask, render_template_string, request
from datetime import datetime, timedelta

app = Flask(__name__)

# 使用 FinMind API 獲取台股資料
def get_finmind_data(ticker, start_date, end_date):
    url = "https://api.finmindtrade.com/v2/data"
    parameter = {
        "dataset": "TaiwanStockPrice",
        "data_id": ticker.replace(".TW", ""),
        "start_date": start_date,
        "end_date": end_date
    }
    try:
        response = requests.get(url, params=parameter)
        data = response.json().get('data', [])
        if not data: return pd.DataFrame()
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        # FinMind 欄位轉換為 Plotly 需要的格式
        df = df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close'})
        return df
    except Exception as e:
        print(f"FinMind Error: {e}")
        return pd.DataFrame()

def get_kline_chart(ticker, title, start_date, end_date):
    df = get_finmind_data(ticker, start_date, end_date)
    if df.empty: return f"<p>無 {title} 資料</p>"
    
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(title=title, xaxis_rangeslider_visible=False, height=400)
    return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>台股官方資料分析</title>
    <style>
        body { font-family: sans-serif; background: #f4f4f9; padding: 20px; }
        .container { max-width: 900px; margin: auto; }
        .chart-box { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>台股分析 (官方 API 來源)</h1>
        <form action="/" method="GET">
            開始: <input type="date" name="start" value="{{ start }}">
            結束: <input type="date" name="end" value="{{ end }}">
            <button type="submit">查詢</button>
        </form>
        <div class="chart-box">{{ index_chart | safe }}</div>
        <div class="chart-box">{{ tsmc_chart | safe }}</div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    end = request.args.get('end', datetime.now().strftime('%Y-%m-%d'))
    start = request.args.get('start', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    
    # FinMind 對台股大盤的 ID 為 '0000'
    index_chart = get_kline_chart("0000", "台股大盤 (加權指數)", start, end)
    tsmc_chart = get_kline_chart("2330", "台積電", start, end)
    
    return render_template_string(HTML_TEMPLATE, index_chart=index_chart, tsmc_chart=tsmc_chart, start=start, end=end)

if __name__ == '__main__':
    app.run(debug=True)