from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf

app = FastAPI()

# Enable CORS (Allows frontend to talk to backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change "*" to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Trading AI backend with CORS enabled is running!"}

@app.get("/stocks/")
def get_multiple_stock_data(tickers: str):
    """
    Fetches stock data for multiple tickers (comma-separated).
    Example: /stocks/?tickers=AAPL,TSLA,GOOG
    """
    try:
        ticker_list = tickers.split(",")  # Convert comma-separated string to a list
        stock_data = {}

        for ticker in ticker_list:
            stock = yf.Ticker(ticker.strip())  # Remove spaces
            data = stock.history(period="1d")

            if data.empty:
                stock_data[ticker] = {"error": "Invalid ticker symbol or no data available"}
            else:
                stock_data[ticker] = {
                    "ticker": ticker.upper(),
                    "last_price": round(data["Close"].iloc[-1], 2),
                    "open_price": round(data["Open"].iloc[-1], 2),
                    "high_price": round(data["High"].iloc[-1], 2),
                    "low_price": round(data["Low"].iloc[-1], 2),
                    "volume": int(data["Volume"].iloc[-1])
                }

        return stock_data
    except Exception as e:
        return {"error": str(e)}