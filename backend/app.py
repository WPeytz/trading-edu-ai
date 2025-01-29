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

@app.get("/stock/{ticker}")
def get_stock_data(ticker: str):
    """
    Fetches stock data from Yahoo Finance.
    """
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d")

        if data.empty:
            return {"error": "Invalid ticker symbol or no data available"}

        return {
            "ticker": ticker.upper(),
            "last_price": round(data["Close"].iloc[-1], 2),
            "open_price": round(data["Open"].iloc[-1], 2),
            "high_price": round(data["High"].iloc[-1], 2),
            "low_price": round(data["Low"].iloc[-1], 2),
            "volume": int(data["Volume"].iloc[-1])
        }
    except Exception as e:
        return {"error": str(e)}