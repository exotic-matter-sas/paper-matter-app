<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the Business Source License. See LICENSE at project root for more information.
  -->

<template>
  <div id="app" class="d-flex flex-column">
    <FTLHeader :account="account" />
    <router-view />
    <FTLFooter />
  </div>
</template>

<!--i18n can't be defined here (it will break i18n defined in other components)-->

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

<style scoped lang="scss">
@import "~bootstrap/scss/_functions.scss";
@import "~bootstrap/scss/_variables.scss";
@import "~bootstrap/scss/_mixins.scss";

#app {
  min-height: 100vh;
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>
