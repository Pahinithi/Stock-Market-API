from fastapi import FastAPI
import requests
import pandas as pd
from pydantic import BaseModel
from .settings import settings


app = FastAPI()


class StockResponse(BaseModel):
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    date: str


def get_stock_data(symbol: str):
    url = f"{settings.base_url}?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={settings.api_key}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 and "Time Series (5min)" in data:
        latest_time = list(data["Time Series (5min)"].keys())[0]
        stock_info = data["Time Series (5min)"][latest_time]

        stock_data = {
            "symbol": symbol,
            "open": float(stock_info["1. open"]),
            "high": float(stock_info["2. high"]),
            "low": float(stock_info["3. low"]),
            "close": float(stock_info["4. close"]),
            "volume": int(stock_info["5. volume"]),
            "date": latest_time,
        }
        return stock_data
    else:
        return None


@app.get("/stock/{symbol}", response_model=StockResponse)
async def get_stock_endpoint(symbol: str):
    stock_data = get_stock_data(symbol)
    if stock_data:
        return stock_data
    else:
        return {"error": "Symbol not found or API request failed"}
