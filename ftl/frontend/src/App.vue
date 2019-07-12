<template>
  <div id="app" class="m-0">
    <header>
      <b-container fluid class="p-0">
        <FTLNavbar :account="account"/>
      </b-container>
    </header>

    <router-view class="content"/>

    <footer>
      <b-container>
        <b-row>
          <b-col>
            {{ this.$_('ftl-app, open source software. Made with ❤ by ') }} <a href="https://www.exotic-matter.fr">Exotic Matter</a>.
          </b-col>
        </b-row>
      </b-container>
    </footer>
  </div>
</template>

<script>
  import FTLNavbar from "@/components/FTLNavbar";

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

    /* Sticky footer */
    display: flex;
    min-height: 100vh;
    flex-direction: column;
  }

  /* Sticky footer */
  .content {
    flex: 1;
  }

  #app > footer {
    background: lightgray;
  }
</style>
