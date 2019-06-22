<template>
  <div id="app">
    <FTLNavbar class="row" :account="account"/>
    <router-view class="row"/>
    <FTLFooter class="row"/>
  </div>
</template>

<script>
  import FTLNavbar from "@/components/FTLNavbar";
  import FTLFooter from "@/components/FTLFooter";

  export default {
    name: "app",
    components: {
      FTLNavbar,
      FTLFooter
    },

    data() {
      return {
        // Misc account stuff
        account: {},
      }
    },

    mounted() {
      // get account value from Django core/home.html template
      let ftlAccountElem = document.getElementById('ftlAccount');
      if (ftlAccountElem) {
        this.account = JSON.parse(ftlAccountElem.textContent);
      }
    }
  }
</script>

<style>
  #app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
</style>
