from flask import Blueprint, jsonify, request
import FinanceDataReader as fdr
import pandas as pd
import datetime

# Blueprint 생성
stock_chart = Blueprint('stock_chart', __name__)

# 종목 이름으로 코드 찾기
def code_from_name(name, df_krx):
    name_list = list(df_krx['Name'])
    return df_krx['Code'][name_list.index(name)]

@stock_chart.route('/api/data', methods=['GET'])
def get_stock_data():
    stock_name = request.args.get('name', 'NAVER')  # 기본값: NAVER
    days_back = 1000  # 가져올 데이터 기간

    # 날짜 계산
    today = datetime.datetime.today()
    start_date = (today - datetime.timedelta(days=days_back)).strftime("%Y%m%d")
    show_from_date = (today - datetime.timedelta(days=365)).strftime("%Y%m%d")

    try:
        print(f"Requested stock name: {stock_name}")
        print("Fetching stock list from KRX...")
        
        # 종목 데이터 가져오기
        df_krx = fdr.StockListing('KRX')
        print(f"KRX stock list loaded: {len(df_krx)} records")
        
        stock_code = code_from_name(stock_name, df_krx)
        print(f"Stock code for {stock_name}: {stock_code}")
        
        df = fdr.DataReader(stock_code, start_date)
        print(f"Stock data fetched for {stock_name} from {start_date}: {len(df)} records")

        # 이동평균선 추가
        for window in [5, 20, 60, 120, 240]:
            df[f'MA{window}'] = df['Close'].rolling(window=window).mean()
        print(f"Moving averages added to stock data for {stock_name}")

        # 날짜 필터링
        df = df[df.index >= show_from_date]
        print(f"Filtered data to include records from {show_from_date}: {len(df)} records")
        print(f"Data snapshot:\n{df.head()}")

        # JSON 데이터 준비
        chart_data = {
            'dates': df.index.strftime('%Y-%m-%d').tolist(),
            'close': df['Close'].tolist(),
            'open': df['Open'].tolist(),
            'high': df['High'].tolist(),
            'low': df['Low'].tolist(),
            'volume': df['Volume'].tolist(),
            'moving_averages': {f'MA{window}': df[f'MA{window}'].tolist() for window in [5, 20, 60, 120, 240]}
        }

        print(f"Prepared JSON data for {stock_name}")
        return jsonify(chart_data)
    except Exception as e:
        print(f"Error occurred while processing {stock_name}: {e}")
        return jsonify({"error": str(e)}), 500