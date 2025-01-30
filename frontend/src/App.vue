<template>
  <div id="app">
    <h1>AI Trading Education Platform</h1>
    <StockDisplay />
    <TradingView />
  </div>
</template>

<script>
import StockDisplay from "./components/StockDisplay.vue";
import TradingView from "./components/TradingView.vue";

export default {
  components: {
    StockDisplay,
    TradingView,
  },
};
</script>

<style>
#app {
  font-family: Arial, sans-serif;
  text-align: center;
  background-color: #121212;
  color: white;
  min-height: 100vh;
  padding-top: 20px;
}
</style>