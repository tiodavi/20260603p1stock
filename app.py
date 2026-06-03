from flask import Flask, render_template_string
import yfinance as yf
import plotly.graph_objects as go
import plotly.io as pio

app = Flask(__name__)

# HTML 模板，包含基本的 CSS 樣式
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>台股即時分析</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; background-color: #f4f4f9; padding: 20px; }
        .container { max-width: 1000px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        .chart { margin-bottom: 40px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>股市資料分析看板</h1>
        <div class="chart">
            <h2>今日台股大盤走勢 (^TWII)</h2>
            {{ index_chart | safe }}
        </div>
        <div class="chart">
            <h2>今日台積電走勢 (2330.TW)</h2>
            {{ tsmc_chart | safe }}
        </div>
    </div>
</body>
</html>
"""

def get_kline_chart(ticker, title):
    # 獲取過去一個月的數據
    df = yf.download(ticker, period="1mo", interval="1d")
    
    # 建立 K 線圖 (Candlestick)
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']
    )])
    
    fig.update_layout(title=title, xaxis_rangeslider_visible=False, height=400)
    
    # 回傳 HTML div 字串
    return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')

@app.route('/')
def index():
    # 獲取圖表 HTML 字串
    index_chart = get_kline_chart("^TWII", "台股大盤")
    tsmc_chart = get_kline_chart("2330.TW", "台積電")
    
    # 渲染頁面
    return render_template_string(HTML_TEMPLATE, index_chart=index_chart, tsmc_chart=tsmc_chart)

if __name__ == '__main__':
    app.run(debug=True)