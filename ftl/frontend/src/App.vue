<template>
  <!--  <div id="app">-->
  <!--    <div id="nav">-->
  <!--      <router-link to="/">Home</router-link> |-->
  <!--      <router-link to="/about">About</router-link>-->
  <!--    </div>-->
  <!--    <router-view/>-->
  <!--  </div>-->

  <div id="app" class="m-0">
    <header>
      <b-container fluid class="p-0">
        <!--        <FTLNavbar :account="account" @event-search="refreshDocumentWithSearch"-->
        <!--                   @event-clear-search="clearSearch"/>        -->
        <FTLNavbar :account="account"/>
      </b-container>
    </header>

    <router-view/>

    <footer>
      <b-container>
        <b-row>
          <b-col>
            {{ this.$_('ftl-app, open source software. Made with ❤ by ') }} <a href="https://www.exotic-matter.fr">Exotic
            Matter</a>.
          </b-col>
        </b-row>
      </b-container>
    </footer>
  </div>
</template>

<script>
  import FTLNavbar from "./components/FTLNavbar";

  export default {
    name: "app",
    components: {
      FTLNavbar
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
    text-align: center;
    color: #2c3e50;
    margin-top: 60px;
  }

  /* Temp for viewing layout */
  div {
    border: 1px dotted;
  }
</style>
