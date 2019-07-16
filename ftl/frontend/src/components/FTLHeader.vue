<template>
  <b-navbar tag="header" toggleable="sm" type="dark" variant="dark">
    <b-navbar-brand href="/app">FTL-APP</b-navbar-brand>

    <b-navbar-nav>
      <router-link :to="{name: 'home'}" tag="b-nav-item">
        <font-awesome-icon icon="home"/>
      </router-link>
      <router-link :to="{name: 'folders'}" tag="b-nav-item">
        <font-awesome-icon icon="folder"/>
      </router-link>
    </b-navbar-nav>

    <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

    <b-collapse id="nav-collapse" is-nav>
      <b-nav-form class="mt-3 mt-sm-0">
        <b-input-group>
          <b-form-input id="search-input" variant="outilne" :placeholder="this.$_('Key words...')"
                        v-model="search"
                        @keydown.enter.prevent="doSearch"
                        required
                        autofocus></b-form-input>

          <b-input-group-append>
            <b-button id="search-button" variant="outline-secondary" type="submit"
                      @click="doSearch">
              {{this.$_('Search')}}
            </b-button>
            <!--
            <b-button size="sm" class="m-1" type="button" variant="secondary"
                      @click="clear">
              {{this.$_('X')}}
            </b-button> -->
          </b-input-group-append>
        </b-input-group>
      </b-nav-form>

      <b-nav-form class="mt-3 mt-sm-0">

      </b-nav-form>
      <b-navbar-nav class="ml-auto">
        <b-nav-item-dropdown right>
          <!-- Using 'button-content' slot -->
          <template slot="button-content"><em id="username">{{ account.name }}</em></template>
          <b-dropdown-item href="/account">{{this.$_('Profile')}}</b-dropdown-item>
          <b-dropdown-item href="/logout">{{this.$_('Sign Out')}}</b-dropdown-item>
        </b-nav-item-dropdown>
      </b-navbar-nav>
    </b-collapse>
  </b-navbar>
</template>

<script>
  export default {
    name: "FTLHeader",

    props: {
      account: {
        type: Object,
        required: true
      }
    },

    data() {
      return {
        search: ""
      }
    },

    methods: {
      clear: function () {
        this.search = "";
        this.doSearch();
      },

      doSearch: function () {
        this.$router.push({name: 'home', query: {q: this.search}})
      }
    }
  }
</script>

<style scoped>
</style>
