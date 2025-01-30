<template>
    <div class="trading-container">
      <h2>Trading Dashboard</h2>
  
      <!-- User Login / Sign Up -->
      <div class="auth-container" v-if="!isLoggedIn">
        <h3>Login or Sign Up</h3>
        <input v-model="username" placeholder="Enter your username" class="input-large" />
        <input type="password" v-model="password" placeholder="Enter your password" class="input-large" />
        <div class="auth-buttons">
          <button @click="loginUser" class="login-btn">Login</button>
          <button @click="signUpUser" class="signup-btn">Sign Up</button>
        </div>
        <p v-if="error" class="error">{{ error }}</p>
      </div>
  
      <!-- Logout & Welcome -->
      <div class="logout-container" v-if="isLoggedIn">
        <p>Welcome, <strong>{{ username }}</strong></p>
        <button class="logout-btn" @click="logoutUser">Logout</button>
      </div>
  
      <!-- Stock Search -->
      <div v-if="isLoggedIn" class="stock-search">
        <input v-model="tickers" placeholder="Enter stock symbols (e.g., AAPL, TSLA, GOOG)" class="input-large" />
        <button class="search-btn" @click="fetchStockData">Search Stocks</button>
      </div>
  
      <!-- Stock Cards -->
      <div v-if="isLoggedIn && Object.keys(stockData).length" class="stocks-grid">
        <div v-for="(data, ticker) in stockData" :key="ticker" class="stock-card">
          <h3>{{ ticker }}</h3>
          <p class="price"><strong>Last Price:</strong> ${{ data.last_price }}</p>
  
          <!-- Trade Actions -->
          <div class="trade-actions">
            <input type="number" v-model="tradeQuantities[ticker]" placeholder="Qty" min="1" class="input-small" />
            <button class="buy-btn" @click="tradeStock(ticker, 'buy')">Buy</button>
            <button class="sell-btn" @click="tradeStock(ticker, 'sell')">Sell</button>
          </div>
        </div>
      </div>
  
      <!-- Portfolio Section -->
      <div class="portfolio-section" v-if="isLoggedIn">
        <h3>My Portfolio</h3>
        <div class="portfolio-list" v-if="Object.keys(portfolio).length">
          <div class="portfolio-card" v-for="(quantity, ticker) in portfolio" :key="ticker">
            <h4>{{ ticker }}</h4>
            <p>{{ quantity }} shares</p>
          </div>
        </div>
        <p v-else class="no-data">No stocks in your portfolio.</p>
      </div>
  
      <!-- Transaction History -->
      <div class="transactions-section" v-if="isLoggedIn">
        <h3>Transaction History</h3>
        <div class="transactions-list" v-if="transactions.length">
          <div class="transaction-card" v-for="(trade, index) in transactions" :key="index">
            <p>
              <span :class="trade.action === 'buy' ? 'buy' : 'sell'">
                {{ trade.action.toUpperCase() }}
              </span>
              {{ trade.quantity }} of {{ trade.ticker }} at ${{ trade.price }}
              <span class="timestamp">on {{ formatTimestamp(trade.timestamp) }}</span>
            </p>
          </div>
        </div>
        <p v-else class="no-data">No transactions yet.</p>
      </div>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  
  export default {
    data() {
      return {
        username: "",
        password: "",
        tickers: "",
        stockData: {},
        tradeQuantities: {},
        portfolio: {},
        transactions: [],
        error: null,
        isLoggedIn: false
      };
    },
    methods: {
      signUpUser() {
        if (!this.username || !this.password) {
          this.error = "Enter a username and password.";
          return;
        }
  
        const users = JSON.parse(localStorage.getItem("users") || "{}");
  
        if (users[this.username]) {
          this.error = "Username already taken.";
          return;
        }
  
        users[this.username] = this.password;
        localStorage.setItem("users", JSON.stringify(users));
  
        this.error = "Account created! Please log in.";
      },
      loginUser() {
        if (!this.username || !this.password) {
          this.error = "Enter both username and password.";
          return;
        }
  
        const users = JSON.parse(localStorage.getItem("users") || "{}");
  
        if (users[this.username] && users[this.username] === this.password) {
          this.isLoggedIn = true;
          localStorage.setItem("username", this.username);
          localStorage.setItem("password", this.password);
          this.fetchPortfolio();
        } else {
          this.error = "Invalid username or password.";
        }
      },
      logoutUser() {
        localStorage.removeItem("username");
        localStorage.removeItem("password");
        this.username = "";
        this.password = "";
        this.isLoggedIn = false;
        this.portfolio = {};
        this.transactions = [];
      },
      async fetchStockData() {
        if (!this.tickers) {
          this.error = "Enter at least one stock ticker.";
          return;
        }
        this.error = null;
        try {
          const response = await axios.get(`http://127.0.0.1:8000/stocks/?tickers=${this.tickers}`);
          this.stockData = response.data;
        } catch (err) {
          this.error = "Failed to fetch stock data.";
        }
      },
      async fetchPortfolio() {
        try {
          const response = await axios.get(`http://127.0.0.1:8000/portfolio/${this.username}`);
          this.portfolio = response.data;
          const transactionsResponse = await axios.get(`http://127.0.0.1:8000/transactions/${this.username}`);
          this.transactions = transactionsResponse.data;
        } catch (err) {
          this.error = "Failed to fetch portfolio or transactions.";
        }
      },
      formatTimestamp(timestamp) {
        if (!timestamp) return "Invalid date";
        const date = new Date(timestamp);
        return date.toLocaleString();
      },
      async tradeStock(ticker, action) {
        if (!this.username || !this.tradeQuantities[ticker]) {
          this.error = "Enter a username and quantity.";
          return;
        }
  
        try {
          console.log(`Trading: ${action} ${this.tradeQuantities[ticker]} of ${ticker}`);
  
          const response = await axios.post("http://127.0.0.1:8000/trade/", {
            username: this.username,
            ticker: ticker,
            quantity: parseInt(this.tradeQuantities[ticker]),
            action: action
          });
  
          console.log("Trade response:", response.data);
  
          if (response.data.error) {
            this.error = response.data.error;
          } else {
            this.portfolio = response.data.portfolio;
            this.transactions = response.data.transaction_history;
          }
        } catch (err) {
          console.error("Trade API Error:", err.response?.data || err.message);
          this.error = "Trade failed. Please try again.";
        }
      }
    },
    mounted() {
      const savedUsername = localStorage.getItem("username");
      const savedPassword = localStorage.getItem("password");
  
      const users = JSON.parse(localStorage.getItem("users") || "{}");
  
      if (savedUsername && users[savedUsername] === savedPassword) {
        this.username = savedUsername;
        this.password = savedPassword;
        this.isLoggedIn = true;
        this.fetchPortfolio();
      }
    }
  };
  </script>
  
  <style scoped>
  .trading-container {
    max-width: 800px;
    margin: auto;
    text-align: center;
    background: #181818;
    color: white;
    padding: 20px;
    border-radius: 10px;
  }
  
  .input-large {
    width: 80%;
    padding: 10px;
    margin: 10px 0;
    font-size: 16px;
    border-radius: 5px;
  }
  
  .input-small {
    width: 60px;
    padding: 5px;
  }
  
  button {
    cursor: pointer;
    padding: 10px;
    margin: 5px;
    border-radius: 5px;
  }
  
  .buy-btn { background: green; color: white; }
  .sell-btn { background: red; color: white; }
  .search-btn { background: blue; color: white; }
  </style>