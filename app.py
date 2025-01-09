from flask import Flask, render_template
from stock_chart import stock_chart  # 위 stock_chart 파일 임포트
from trade_api import trade_api  # 매수/매도 API 임포트

app = Flask(__name__)

# 블루프린트 등록
app.register_blueprint(stock_chart, url_prefix='/stock')
app.register_blueprint(trade_api, url_prefix='/api')

@app.route('/chart')
def chart():
    # chart.html 템플릿 렌더링
    return render_template('stock_chart.html')

@app.route('/trade')
def trade():
    return render_template('trade.html')

if __name__ == '__main__':
    app.run(debug=True)