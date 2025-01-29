<template>
    <div class="stock-container">
      <h2>Stock Price Lookup</h2>
  
      <input v-model="ticker" placeholder="Enter stock symbol (e.g., AAPL)" />
      <button @click="fetchStockData">Get Stock Data</button>
  
      <div v-if="stockData">
        <h3>{{ stockData.ticker }} Stock Data</h3>
        <p><strong>Last Price:</strong> ${{ stockData.last_price }}</p>
        <p><strong>Open Price:</strong> ${{ stockData.open_price }}</p>
        <p><strong>High Price:</strong> ${{ stockData.high_price }}</p>
        <p><strong>Low Price:</strong> ${{ stockData.low_price }}</p>
        <p><strong>Volume:</strong> {{ stockData.volume }}</p>
      </div>
  
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  
  export default {
    data() {
      return {
        ticker: "",
        stockData: null,
        error: null,
      };
    },
    methods: {
      async fetchStockData() {
        if (!this.ticker) {
          this.error = "Please enter a stock ticker symbol.";
          return;
        }
  
        this.error = null;
        this.stockData = null;
  
        try {
          const response = await axios.get(`http://127.0.0.1:8000/stock/${this.ticker}`);
          this.stockData = response.data;
          
          if (response.data.error) {
            this.error = response.data.error;
            this.stockData = null;
          }
        } catch (err) {
          this.error = "Failed to fetch stock data. Please try again.";
        }
      },
    },
  };
  </script>
  
  <style scoped>
    .stock-container {
    max-width: 400px;
    margin: auto;
    text-align: center;
    padding: 20px;
    border: 1px solid #ccc;
    border-radius: 8px;
    background-color: #f9f9f9;
    color: black; /* Ensures all text is visible */
    }

    h3, p {
    color: black !important; /* Force visibility */
    }

  input {
    width: 80%;
    padding: 8px;
    margin: 10px 0;
  }
  
  button {
    background-color: #007bff;
    color: white;
    padding: 10px;
    border: none;
    cursor: pointer;
  }
  
  button:hover {
    background-color: #0056b3;
  }
  
  .error {
    color: red;
    font-weight: bold;
  }
  </style>