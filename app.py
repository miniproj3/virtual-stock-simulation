from flask import Flask, render_template
from stock_chart import stock_chart

app = Flask(__name__)

# 블루프린트 등록
app.register_blueprint(stock_chart, url_prefix='/stock')

@app.route('/chart')
def chart():
    # chart.html 템플릿 렌더링
    return render_template('stock_chart.html')

if __name__ == '__main__':
    app.run(debug=True)