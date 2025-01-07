from flask import *
import requests

stock_us = Blueprint('stock_us', __name__)


# def fetch_us_stock_data():
#     url = "https://query1.finance.yahoo.com/v7/finance/quote?symbols=005930.KQ,000660.KQ,035420.KQ"
#     response = requests.get(url)
#     if response.status_code == 200:
#         data = response.json()
#         return data['quoteResponse']['result']
#     else:
#         return []
