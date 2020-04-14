<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <div id="app" class="d-flex flex-column">
    <FTLHeader :account="account" />
    <router-view />
    <FTLFooter />
  </div>
</template>

<script>
import FTLHeader from "@/components/FTLHeader";
import FTLFooter from "@/components/FTLFooter";

export default {
  name: "app",
  components: {
    FTLHeader,
    FTLFooter,
  },

  data() {
    return {
      // Misc account stuff
      account: {},
    };
  },

  mounted: function () {
    // get account value from Django core/home.html template
    let ftlAccountElem = document.getElementById("ftlAccount");
    if (ftlAccountElem) {
      this.account = JSON.parse(ftlAccountElem.textContent);
      this.$store.commit("setFtlAccount", this.account);
    }
    // get locale value from Django core/home.html template
    const localeElem = document.getElementById("locale");
    if (localeElem) {
      this.$i18n.locale = JSON.parse(localeElem.textContent);
    }
  },
};
</script>

<style lang="scss">
@import "~bootstrap/scss/_functions.scss";
@import "~bootstrap/scss/_variables.scss";
@import "~bootstrap/scss/_mixins.scss";

#app {
  min-height: 100vh;
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

// ANIMATIONS
@keyframes unspin {
  to {
    transform: rotate(-0.5turn);
  }
}

@keyframes slide-down {
  from {
    transform: translateY(-30px);
    opacity: 0;
  }
  to {
    transform: translateY(0px);
    opacity: 1;
  }
}
</style>
