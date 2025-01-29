<template>
  <div id="app">
    <h1>AI Trading Education Platform</h1>
    <StockDisplay />
  </div>
</template>

<script>
import StockDisplay from "./components/StockDisplay.vue";

export default {
  components: {
    StockDisplay,
  },
};
</script>

<style>
#app {
  font-family: Arial, sans-serif;
  text-align: center;
}
</style>