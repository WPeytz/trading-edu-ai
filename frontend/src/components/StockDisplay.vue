<template>
  <div class="stock-container">
    <h2>Stock Price Lookup</h2>

    <div class="input-group">
      <input v-model="tickers" placeholder="Enter symbols (e.g., AAPL, TSLA, GOOG)" />
      <button @click="fetchStockData">Get Stock Data</button>
      <button @click="saveFavorites">Save Favorites</button>
    </div>

    <div v-if="Object.keys(stockData).length" class="stocks-grid">
      <div v-for="(data, ticker) in stockData" :key="ticker" class="stock-card">
        <h3>{{ ticker }} Stock</h3>
        <p>
          <strong>Last Price:</strong>
          <span
            :class="[getPriceChangeClass(ticker), 'price-value']"
            :key="data.last_price"
          >
            ${{ data.last_price }}
            <span v-if="priceChanges[ticker] !== null">
              ({{ priceChanges[ticker] > 0 ? '▲' : '▼' }} {{ Math.abs(priceChanges[ticker]).toFixed(2) }})
            </span>
          </span>
        </p>
        <p><strong>Open Price:</strong> ${{ data.open_price }}</p>
        <p><strong>High Price:</strong> ${{ data.high_price }}</p>
        <p><strong>Low Price:</strong> ${{ data.low_price }}</p>
        <p><strong>Volume:</strong> {{ data.volume }}</p>
      </div>
    </div>

    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      tickers: "", // User input
      stockData: {}, // Stores stock data
      previousPrices: {}, // Tracks previous prices for change comparison
      priceChanges: {}, // Tracks price differences
      error: null,
      refreshInterval: null,
    };
  },
  methods: {
    async fetchStockData() {
      if (!this.tickers) {
        this.error = "Please enter at least one stock ticker symbol.";
        return;
      }

      this.error = null;

      try {
        console.log(`Fetching data for: ${this.tickers}`); // Debugging
        const response = await axios.get(`http://127.0.0.1:8000/stocks/?tickers=${this.tickers}`);
        
        console.log("API Response:", response.data); // Debugging
        
        if (!response.data) {
          this.error = "No data received.";
        } else {
          // Update price changes
          Object.keys(response.data).forEach((ticker) => {
            const newPrice = response.data[ticker].last_price;
            if (this.previousPrices[ticker] !== undefined) {
              this.priceChanges[ticker] = newPrice - this.previousPrices[ticker];
            }
            this.previousPrices[ticker] = newPrice;
          });

          this.stockData = response.data;
        }
      } catch (err) {
        console.error("API Error:", err);
        this.error = "Failed to fetch stock data. Please try again.";
      }
    },
    startAutoRefresh() {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval);
      }

      this.refreshInterval = setInterval(() => {
        console.log("Auto-refreshing stock data...");
        this.fetchStockData();
      }, 60000);
    },
    getPriceChangeClass(ticker) {
      if (!this.priceChanges[ticker]) return "";
      return this.priceChanges[ticker] > 0 ? "price-up" : "price-down";
    },
    saveFavorites() {
      localStorage.setItem("favoriteStocks", this.tickers);
      alert("Saved favorite stocks!");
    },
    loadFavorites() {
      const savedTickers = localStorage.getItem("favoriteStocks");
      if (savedTickers) {
        this.tickers = savedTickers;
        this.fetchStockData(); // Load data on startup
      }
    }
  },
  watch: {
    tickers(newTickers) {
      if (newTickers) {
        this.startAutoRefresh();
      }
    }
  },
  mounted() {
    this.loadFavorites(); // Load favorite stocks when component loads
    this.startAutoRefresh();
  },
  beforeUnmount() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  }
};
</script>

<style scoped>
/* Container Styling */
.stock-container {
  max-width: 800px;
  margin: auto;
  text-align: center;
  padding: 20px;
  border-radius: 10px;
  background-color: #222;
  color: white;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
}

/* Input Group */
.input-group {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 20px;
}

input {
  width: 50%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: #333;
  color: white;
}

/* Button Styling */
button {
  background-color: #007bff;
  color: white;
  padding: 10px 15px;
  border: none;
  cursor: pointer;
  border-radius: 5px;
  transition: 0.3s ease-in-out;
}

button:hover {
  background-color: #0056b3;
}

/* Stocks Grid */
.stocks-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  justify-content: center;
}

/* Stock Card */
.stock-card {
  background-color: #333;
  padding: 15px;
  border-radius: 8px;
  width: 250px;
  text-align: left;
  box-shadow: 0px 2px 5px rgba(255, 255, 255, 0.1);
}

h3 {
  text-align: center;
  color: #ffcc00;
  margin-bottom: 10px;
}

p {
  font-size: 14px;
  line-height: 1.5;
  color: #ddd;
}

/* Price Change Colors & Animations */
.price-value {
  transition: color 0.5s ease-in-out;
}

.price-up {
  color: #00ff00; /* Green for price increase */
  font-weight: bold;
  animation: pulse-green 0.5s ease-in-out;
}

.price-down {
  color: #ff3333; /* Red for price decrease */
  font-weight: bold;
  animation: pulse-red 0.5s ease-in-out;
}

/* Green Pulse Animation */
@keyframes pulse-green {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); color: #66ff66; }
  100% { transform: scale(1); }
}

/* Red Pulse Animation */
@keyframes pulse-red {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); color: #ff6666; }
  100% { transform: scale(1); }
}

.error {
  color: red;
  font-weight: bold;
  margin-top: 15px;
}
</style>