from flask import Flask, render_template_string
import yfinance as yf
import plotly.graph_objects as go
import plotly.io as pio

app = Flask(__name__)

def get_kline_chart(ticker, title):
    # 獲取今日與過去的數據
    df = yf.download(ticker, period="1mo", interval="1d")
    
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']
    )])
    
    fig.update_layout(title=title, xaxis_rangeslider_visible=False)
    # 將圖表轉為 HTML div 字串，方便嵌入網頁
    return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')

@app.route('/')
def index():
    # ^TWII 是台股大盤代碼, 2330.TW 是台積電
    index_chart = get_kline_chart("^TWII", "台股大盤走勢")
    tsmc_chart = get_kline_chart("2330.TW", "台積電 (2330) 走勢")
    
    html = f"""
    <html>
        <head><title>台股分析儀表板</title></head>
        <body>
            <h1>台股即時走勢</h1>
            <div>{index_chart}</div>
            <div>{tsmc_chart}</div>
        </body>
    </html>
    """
    return html

if __name__ == '__main__':
    app.run(debug=True)