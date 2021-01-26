<!--
  - Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
  - Licensed under the Business Source License. See LICENSE at project root for more information.
  -->

<template>
  <b-navbar tag="header" toggleable="sm" type="dark" variant="dark">
    <b-navbar-brand href="/app">
      <img src="@/assets/grays_logo.svg" alt="PM Logo" class="pm-logo" />
    </b-navbar-brand>

    <b-nav-form id="search-form">
      <b-input-group id="search-zone">
        <b-form-input
          id="search-input"
          variant="outilne"
          :placeholder="$t('Keywords...')"
          v-model="search"
          @keydown.enter.prevent="doSearch"
          required
          autofocus
        ></b-form-input>

        <b-input-group-append>
          <b-button
            id="search-button"
            variant="outline-secondary"
            type="submit"
            @click.prevent="doSearch"
            :disabled="search === ''"
          >
            <span class="d-none d-lg-inline">{{ $t("Search") }}</span>
            <font-awesome-icon class="d-lg-none" icon="search" size="sm" />
          </b-button>
        </b-input-group-append>
      </b-input-group>
    </b-nav-form>

    <b-navbar-toggle class="ml-2" target="nav-collapse"></b-navbar-toggle>

    <b-collapse id="nav-collapse" is-nav>
      <b-nav-form class="mt-3 ml-0 mt-sm-0 ml-sm-2">
        <b-dropdown
          id="add-documents"
          right
          split
          variant="outline-secondary"
          :html="`<label for='upload-doc-input' class='m-0'>${addDocumentsButtonText}</label>`"
        >
          <b-dropdown-item
            :href="$t('https://welcome.papermatter.app/downloads')"
            target="_blank"
            :title="
              $t(
                'Import a folder or a large amount of documents using the local import client'
              )
            "
          >
            {{ $t("Import a folder") }}
            <font-awesome-icon icon="external-link-alt" size="sm" />
          </b-dropdown-item>
        </b-dropdown>
      </b-nav-form>

      <b-navbar-nav class="ml-auto">
        <b-nav-item-dropdown right class="px-0">
          <template slot="button-content">
            <font-awesome-icon
              v-if="account.isSuperUser"
              icon="crown"
              class="super-user"
              title="Super User"
            />
            <em id="email">{{ account.name }}</em>
            <b-badge
              v-if="account.otp_warning"
              variant="danger"
              class="m-1 otp-warning"
              pill="true"
              >!</b-badge
            >
          </template>
          <b-dropdown-item v-if="account.isSuperUser" href="/admin">
            {{ $t("Admin") }}
          </b-dropdown-item>
          <b-dropdown-item href="/accounts">
            {{ $t("Settings") }}
            <b-badge
              v-if="account.otp_warning"
              variant="danger"
              class="m-1 otp-warning"
              pill="true"
              >!</b-badge
            >
          </b-dropdown-item>
          <b-dropdown-item href="/logout">{{ $t("Sign Out") }}</b-dropdown-item>
        </b-nav-item-dropdown>
      </b-navbar-nav>
    </b-collapse>
  </b-navbar>
</template>

<i18n>
  fr:
    Home: Accueil
    Folders management: Gestion des dossiers
    Keywords...: Mots clés...
    Search: Rechercher
    Add documents: Ajouter des documents
    Add documents to root: Ajouter des documents à la racine
    Import a folder: Importer un dossier
    Import a folder or a large amount of documents using the local import client: Importer un dossier ou un grand nombre de documents en utilisant le client d'import local
    "https://welcome.papermatter.app/downloads": "https://welcome.papermatter.app/fr/downloads"
    Settings: Paramètres
    Sign Out: Se déconnecter
    Admin: Administration
</i18n>

<script>
export default {
  name: "FTLHeader",

  props: {
    account: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      search: "",
    };
  },

  watch: {
    $route(to, from) {
      this.update();
    },
  },

  computed: {
    addDocumentsButtonText: function () {
      return this.$route.name === "home-search"
        ? this.$t("Add documents to root")
        : this.$t("Add documents");
    },
  },

  mounted() {
    this.update();
  },

  methods: {
    clear: function () {
      this.search = "";
      this.$router.push({ name: "home" });
    },

    update: function () {
      if (this.$route.params.search) {
        this.search = this.$route.params.search;
      } else {
        this.search = "";
      }
    },

    doSearch: function () {
      if (this.search !== "") {
        this.$router.push({
          name: "home-search",
          params: { search: this.search },
        });
      }
    },
  },
};
</script>

<style scoped lang="scss">
@import "~bootstrap/scss/_functions.scss";
@import "~bootstrap/scss/_variables.scss";
@import "~bootstrap/scss/_mixins.scss";

#search-input {
  width: 120px;
  margin: 0;

  &:invalid {
    box-shadow: none;
  }
}

/* Custom breakpoint used to fine tune search bar responsive */
@media (min-width: 400px) {
  #search-input {
    width: 1%; // default width set by bootstrap
  }
}

@include media-breakpoint-up(lg) {
  #search-input {
    margin-left: 0.5rem;
    width: 25vw;
  }
}

.super-user {
  color: #d0d8d9;
  margin-right: 0.5em;
  font-size: 0.7em;
}

::v-deep #add-documents > button:first-child {
  padding: 0;

  label {
    padding: 0.375rem 0.75rem;
    cursor: pointer;
  }
}
</style>
