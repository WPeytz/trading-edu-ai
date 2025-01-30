from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yfinance as yf
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import DateTime
from datetime import datetime
import os

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# **Database Configuration**
DB_URL = "sqlite:///./trading.db"  # Use SQLite
# DB_URL = "postgresql://user:password@localhost/tradingdb"  # Use PostgreSQL if needed

engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if "sqlite" in DB_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# **Database Models**
class UserPortfolio(Base):
    __tablename__ = "portfolios"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    ticker = Column(String, index=True)
    quantity = Column(Integer, default=0)

class TradeHistory(Base):
    __tablename__ = "trade_history"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    ticker = Column(String)
    quantity = Column(Integer)
    price = Column(Float)
    action = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency for getting DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# **Pydantic Model for Trade Requests**
class TradeRequest(BaseModel):
    username: str
    ticker: str
    quantity: int
    action: str

@app.get("/")
def read_root():
    return {"message": "Trading API is running"}

@app.get("/stocks/")
def get_multiple_stock_data(tickers: str):
    """
    Fetch stock prices for multiple tickers.
    Example: /stocks/?tickers=AAPL,TSLA,GOOG
    """
    ticker_list = tickers.split(",")
    stock_data = {}

    for ticker in ticker_list:
        stock = yf.Ticker(ticker.strip())
        data = stock.history(period="1d")

        if data.empty:
            stock_data[ticker] = {"error": "Invalid ticker symbol or no data available"}
        else:
            stock_data[ticker] = {
                "ticker": ticker.upper(),
                "last_price": round(data["Close"].iloc[-1], 2),
            }

    return stock_data

@app.post("/trade/")
def trade_stock(trade: TradeRequest, db: Session = Depends(get_db)):
    """
    Handles buy/sell transactions with timestamps.
    """
    username, ticker, quantity, action = trade.username, trade.ticker, trade.quantity, trade.action

    print(f"Trade request received: {action} {quantity} {ticker} for {username}")

    if action not in ["buy", "sell"]:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'buy' or 'sell'.")

    # Get stock price
    stock = yf.Ticker(ticker)
    data = stock.history(period="1d")

    if data.empty:
        raise HTTPException(status_code=400, detail="Invalid ticker symbol or no data available")

    last_price = round(data["Close"].iloc[-1], 2)

    # **Check existing user holdings**
    existing = db.query(UserPortfolio).filter_by(username=username, ticker=ticker).first()

    if action == "buy":
        if existing:
            existing.quantity += quantity
        else:
            new_entry = UserPortfolio(username=username, ticker=ticker, quantity=quantity)
            db.add(new_entry)
    elif action == "sell":
        if not existing or existing.quantity < quantity:
            raise HTTPException(status_code=400, detail="Insufficient shares to sell")
        existing.quantity -= quantity
        if existing.quantity == 0:
            db.delete(existing)

    # **Log transaction with timestamp**
    trade_entry = TradeHistory(
        username=username, 
        ticker=ticker, 
        quantity=quantity, 
        price=last_price, 
        action=action, 
        timestamp=datetime.utcnow()  # ✅ Store trade time
    )
    db.add(trade_entry)

    db.commit()

    return {
        "message": f"Successfully {action}ed {quantity} shares of {ticker} at ${last_price} per share",
        "portfolio": get_portfolio(username, db),
        "transaction_history": get_trade_history(username, db)
    }

@app.get("/portfolio/{username}")
def get_portfolio(username: str, db: Session = Depends(get_db)):
    """Returns the user's portfolio"""
    portfolio = db.query(UserPortfolio).filter_by(username=username).all()
    return {item.ticker: item.quantity for item in portfolio}

@app.get("/transactions/{username}")
def get_trade_history(username: str, db: Session = Depends(get_db)):
    """Returns the user's trade history with timestamps"""
    transactions = db.query(TradeHistory).filter_by(username=username).all()
    return [
        {
            "ticker": t.ticker,
            "quantity": t.quantity,
            "price": t.price,
            "action": t.action,
            "timestamp": t.timestamp.strftime("%Y-%m-%d %H:%M:%S")  # ✅ Format timestamp
        } 
        for t in transactions
    ]