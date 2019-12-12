<!--
  - Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <div id="app" class="d-flex flex-column">
    <FTLHeader :account="account"/>
    <router-view/>
    <FTLFooter/>
  </div>
</template>

<script>
  import FTLHeader from "@/components/FTLHeader";
  import FTLFooter from "@/components/FTLFooter";

  export default {
    name: "app",
    components: {
      FTLHeader,
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
    min-height: 100vh;
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
</style>
