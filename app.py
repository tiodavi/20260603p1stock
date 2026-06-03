import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
from flask import Flask, render_template_string, request
from flask_caching import Cache
from datetime import datetime, timedelta

app = Flask(__name__)
# 設定快取：將資料快取 6 小時，減少 API 呼叫次數
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

def get_market_chart(ticker, title, start, end):
    df = yf.download(ticker, start=start, end=end, progress=False)
    if df.empty: return None

    # 建立雙軸圖表 (上: K線, 下: 成交量)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.03, subplot_titles=(title, '成交量'),
                        row_width=[0.2, 0.7])

    # 繪製 K 線
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], 
                                 low=df['Low'], close=df['Close'], name='Price'), row=1, col=1)
    
    # 繪製成交量
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='blue'), row=2, col=1)

    fig.update_layout(height=600, xaxis_rangeslider_visible=False, showlegend=False)
    return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <title>專業股市分析平台</title>
</head>
<body class="bg-light">
    <div class="container py-4">
        <h1 class="mb-4 text-center">📈 專業股市分析儀表板</h1>
        <form method="GET" class="row g-3 mb-4 p-3 bg-white shadow-sm rounded">
            <div class="col-md-5"><label>開始日期</label><input type="date" name="start" class="form-control" value="{{ start }}"></div>
            <div class="col-md-5"><label>結束日期</label><input type="date" name="end" class="form-control" value="{{ end }}"></div>
            <div class="col-md-2 d-flex align-items-end"><button class="btn btn-primary w-100">查詢</button></div>
        </form>
        <div class="card p-3 mb-4">{{ chart_idx | safe }}</div>
        <div class="card p-3">{{ chart_tsmc | safe }}</div>
    </div>
</body>
</html>
"""

@app.route('/')
@cache.cached(timeout=21600, query_string=True) # 快取 6 小時
def index():
    end = request.args.get('end', datetime.now().strftime('%Y-%m-%d'))
    start = request.args.get('start', (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d'))
    
    chart_idx = get_market_chart("^TWII", "台股大盤", start, end)
    chart_tsmc = get_market_chart("2330.TW", "台積電", start, end)
    
    return render_template_string(HTML_TEMPLATE, chart_idx=chart_idx, chart_tsmc=chart_tsmc, start=start, end=end)

if __name__ == '__main__':
    app.run(debug=True)