<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <main class="flex-grow">
    <b-col>
      <b-row>
        <b-col>
          <FTLUpload :files-to-upload.sync="droppedFiles" />
        </b-col>
      </b-row>

      <b-row class="my-3" id="breadcrumb" no-gutter>
        <b-col>
          <b-breadcrumb class="breadcrumb-ftl m-0">
            <FTLBreadcrumbFolder
              v-for="(item, index) in breadcrumbPlaceholder"
              :key="item.id"
              :id="item.id"
              :text="item.text"
              :to="item.to"
              :active="index === breadcrumbPlaceholder.length - 1"
              :folder="{ id: item.id, name: item.text }"
            />
          </b-breadcrumb>
        </b-col>
      </b-row>

      <b-row
        v-show="!selectedDocumentsHome.length"
        class="mt-3"
        id="folders-list"
      >
        <b-col class="text-center">
          <b-button
            id="refresh-documents"
            class="float-left"
            :disabled="docsLoading"
            variant="primary"
            @click="updateDocuments"
          >
            <font-awesome-icon
              icon="sync"
              :spin="docsLoading"
              :class="{ 'stop-spin': !docsLoading }"
              :title="$t('Refresh documents list')"
            />
          </b-button>

          <span v-if="count > 0" id="documents-count" class="text-muted">{{
            $tc("| 1 result found | {n} results found", count)
          }}</span>

          <b-dropdown
            id="documents-sort"
            right
            variant="link"
            class="m-1 text-decoration-none"
          >
            <template slot="button-content">
              <font-awesome-icon icon="sort" />
              {{ $t("Sort") }}
              <span v-if="sort === 'az'">({{ $t("A-Z") }})</span>
              <span v-else-if="sort === 'za'">({{ $t("Z-A") }})</span>
              <span v-else-if="sort === 'recent'"
                >({{ $t("Recent first") }})</span
              >
              <span v-else-if="sort === 'older'"
                >({{ $t("Older first") }})</span
              >
              <span v-else-if="sort === 'relevance'"
                >({{ $t("Relevance") }})</span
              >
            </template>
            <b-dropdown-item-button
              id="az-sort"
              href="#"
              @click.prevent="sort = 'az'"
              >{{ $t("A-Z") }}&nbsp;
              <span v-if="sort === 'az'"
                >&checkmark;</span
              ></b-dropdown-item-button
            >
            <b-dropdown-item-button
              id="za-sort"
              href="#"
              @click.prevent="sort = 'za'"
              >{{ $t("Z-A") }}&nbsp;
              <span v-if="sort === 'za'"
                >&checkmark;</span
              ></b-dropdown-item-button
            >
            <b-dropdown-divider />
            <b-dropdown-item-button
              id="recent-sort"
              href="#"
              @click.prevent="sort = 'recent'"
              >{{ $t("Recent first") }}&nbsp;
              <span v-if="sort === 'recent'"
                >&checkmark;</span
              ></b-dropdown-item-button
            >
            <b-dropdown-item-button
              id="older-sort"
              href="#"
              @click.prevent="sort = 'older'"
              >{{ $t("Older first") }}&nbsp;
              <span v-if="sort === 'older'"
                >&checkmark;</span
              ></b-dropdown-item-button
            >
            <b-dropdown-item-button
              id="relevance-sort"
              href="#"
              @click.prevent="sort = 'relevance'"
              >{{ $t("Relevance") }}&nbsp;
              <span v-if="sort === 'relevance'"
                >&checkmark;</span
              ></b-dropdown-item-button
            >
          </b-dropdown>
        </b-col>
      </b-row>

      <b-row
        v-show="selectedDocumentsHome.length"
        class="mb-3"
        id="action-selected-documents"
      >
        <b-col>
          <b-button
            v-if="docs.length === selectedDocumentsHome.length"
            id="unselect-all-documents"
            variant="outline-primary"
            @click="$store.commit('unselectAllDocuments')"
            :title="$t('Deselect all documents')"
          >
            {{ $t("Deselect all") }}
          </b-button>
          <b-button
            v-else
            id="select-all-documents"
            variant="outline-primary"
            :title="$t('Select all documents displayed')"
            @click="$store.commit('selectDocuments', docs)"
          >
            {{ $t("Select all") }}
          </b-button>
        </b-col>
        <b-col cols="7" class="text-right">
          <span class="text-muted d-none d-sm-inline d-md-none">{{
            $tc("| 1 doc: | {n} docs:", selectedDocumentsHome.length)
          }}</span>
          <span class="text-muted d-none d-md-inline">{{
            $tc("| 1 document: | {n} documents:", selectedDocumentsHome.length)
          }}</span>
          <b-button
            id="cancel-selection"
            class="d-none d-md-inline-block"
            @click="$store.commit('unselectAllDocuments')"
            :title="$t('Deselect all documents')"
          >
            {{ $t("Cancel") }}
          </b-button>
          <b-button
            id="move-documents"
            variant="primary"
            v-b-modal="'modal-move-documents-hs'"
            :title="$t('Move to folder')"
          >
            <font-awesome-icon icon="folder-open" class="d-sm-none" />
            <span class="d-none d-sm-inline">{{ $t("Move") }}</span>
          </b-button>
          <b-button
            id="delete-documents"
            variant="danger"
            v-b-modal="'modal-delete-documents-hs'"
            :title="$t('Delete documents')"
          >
            <font-awesome-icon icon="trash" class="d-sm-none" />
            <span class="d-none d-sm-inline">{{ $t("Delete") }}</span>
          </b-button>
        </b-col>
      </b-row>

      <b-row
        class="mt-2 mb-3"
        id="documents-list"
        :class="{ 'documents-list-dragged-hover': draggingFilesToDocsList }"
        @dragenter="showDropZone"
        @dragover="allowDrop"
        @drop="getDroppedFiles"
        @dragleave.self="hideDropZone"
      >
        <b-col v-if="docsLoading">
          <b-spinner
            class="mx-auto loader"
            id="documents-list-loader"
            label="Loading..."
          ></b-spinner>
        </b-col>
        <b-col v-else-if="docs.length">
          <b-row tag="section">
            <FTLDocument
              v-for="doc in docs"
              :key="doc.pid"
              :doc="doc"
              @event-open-doc="navigateToDocument"
              @event-rename-doc="renameDoc"
            />
          </b-row>
        </b-col>
        <b-col v-else class="text-center">{{ $t("No result found") }}</b-col>
        <div
          v-show="draggingFilesToDocsList"
          id="document-drop-overlay"
          class="position-fixed w-100 text-center font-weight-bold"
        >
          <div id="document-drop-label" class="w-100 my-5">
            <img
              class="mb-3"
              src="@/assets/add_files.svg"
              alt="Add files illustration"
            />
            <br />
            <p class="mb-3">{{ $t("Drop documents to upload to root.") }}</p>
          </div>
        </div>
      </b-row>

      <b-row v-if="moreDocs" align-h="center" class="my-3">
        <b-col>
          <b-button
            id="more-documents"
            block
            variant="secondary"
            @click.prevent="loadMoreDocuments"
          >
            <b-spinner
              class="loader"
              :class="{ 'd-none': !moreDocsLoading }"
              small
            ></b-spinner>
            <span :class="{ 'd-none': moreDocsLoading }">{{
              $tc(
                "| Show more documents (1 remaining) | Show more documents ({n} remaining)",
                count - docs.length
              )
            }}</span>
          </b-button>
        </b-col>
      </b-row>

      <b-row v-else-if="count > 0" class="my-3">
        <b-col>
          <p class="text-center">
            {{ $t("No more search results") }}
          </p>
        </b-col>
      </b-row>

      <!-- Pdf viewer popup -->
      <FTLDocumentPanel
        v-if="docPid"
        :pid="docPid"
        :search="currentSearch"
        @event-document-panel-closed="documentClosed"
        @event-document-moved="documentDeleted"
        @event-document-deleted="documentDeleted"
      />

      <!-- For batch action move document -->
      <FTLMoveDocuments
        v-if="selectedDocumentsHome.length > 0"
        modal-id="modal-move-documents-hs"
        :docs="selectedDocumentsHome"
        @event-document-moved="documentDeleted"
      />

      <FTLDeleteDocuments
        v-if="selectedDocumentsHome.length > 0"
        modal-id="modal-delete-documents-hs"
        :docs="selectedDocumentsHome"
        @event-document-deleted="documentDeleted"
      />

      <FTLRenameDocument
        modal-id="modal-rename-document-hs"
        :doc="currentRenameDoc"
        @event-document-renamed="documentUpdated"
      />
    </b-col>
  </main>
</template>

<i18n>
  fr:
    Root: Racine
    Search results: Résultats de la recherche
    Refresh documents list: Rafraichir la liste des documents
    Sort: Trier
    Recent first: Récents en premier
    Older first: Anciens en premier
    Relevance: Pertinence
    A-Z: A-Z
    Z-A: Z-A
    Select all: Tout sélectionner
    Deselect all: Tout désélectionner
    "| 1 doc: | {n} docs:": "| 1 doc : | {n} docs :"
    "| 1 document: | {n} documents:": "| 1 document : | {n} documents :"
    "| 1 result found | {n} results found": "| 1 résultat | {n} résultats"
    No result found: Aucun résultat
    "| Show more documents (1 remaining) | Show more documents ({n} remaining)": "| Afficher plus de documents (1 restant) | Afficher plus de documents ({n} restants)"
    No more search results: Plus aucun résultat à afficher
    Could not open this folder.: Impossible d'ouvrir ce dossier.
    Select all documents displayed: Sélectionner tous les documents affichés
    Deselect all documents: Désélectionner tous les documents
    Move to folder: Déplacer vers le dossier
    Delete documents: Supprimer les documents
    Drop documents to upload to root.: Déposez les documents pour les ajouter à la racine.
</i18n>

<script>
// @ is an alias to /src
import { mapState } from "vuex";
import HomeBase from "@/views/HomeBase";
import FTLDocumentPanel from "@/components/FTLDocumentPanel";
import FTLDeleteDocuments from "@/components/FTLDeleteDocuments";
import FTLMoveDocuments from "@/components/FTLMoveDocuments";
import FTLDocument from "@/components/FTLDocument";
import FTLUpload from "@/components/FTLUpload";
import FTLRenameDocument from "@/components/FTLRenameDocument";
import FTLBreadcrumbFolder from "@/components/FTLBreadcrumbFolder";

export default {
  name: "home-search",
  extends: HomeBase,

  components: {
    FTLDocumentPanel,
    FTLDeleteDocuments,
    FTLMoveDocuments,
    FTLDocument,
    FTLUpload,
    FTLRenameDocument,
    FTLBreadcrumbFolder,
  },

  props: ["searchQuery"],

  data() {
    return {
      sort: "relevance",
      currentSearch: "",
    };
  },

  mounted() {
    if (this.searchQuery) {
      // search docs
      this.refreshDocumentWithSearch(this.searchQuery);
    } else {
      // all docs
      this.updateDocuments();
    }

    // Clear the selected documents
    this.$store.commit("unselectAllDocuments");
  },

  watch: {
    searchQuery: function (newVal, oldVal) {
      if (newVal !== oldVal) {
        this.refreshDocumentWithSearch(newVal);
      }

      // Clear the selected documents
      this.$store.commit("unselectAllDocuments");
    },
    sort: function (newVal, oldVal) {
      if (newVal !== oldVal) {
        this.updateDocuments();
      }
    },
  },

  computed: {
    breadcrumbPlaceholder: function () {
      return [
        {
          id: null,
          text: this.$t("Root"),
          to: { name: "home" },
        },
        {
          id: -1,
          text: this.$t("Search results"),
          to: { name: "home" },
        },
      ];
    },

    ...mapState(["selectedDocumentsHome"]), // generate computed for vuex getters
  },

  methods: {
    refreshDocumentWithSearch: function (text) {
      this.currentSearch = text;
      this.sort = "relevance"; // reset sort to relevance for new search
      this.updateDocuments();
    },

    updateDocuments: function () {
      let queryString = {};

      if (this.currentSearch !== null && this.currentSearch !== "") {
        queryString["search"] = this.currentSearch;
      }

      return this._updateDocuments(queryString);
    },

    renameDoc: function (doc) {
      this.currentRenameDoc = doc;
      this.$bvModal.show("modal-rename-document-hs");
    },
  },
};
</script>

<style scoped lang="scss">
@import "~bootstrap/scss/_functions.scss";
@import "~bootstrap/scss/_variables.scss";
@import "~bootstrap/scss/_mixins.scss";

#documents-list {
  min-height: 400px;
}

#documents-list-loader {
  width: 3em;
  height: 3em;
  display: block;
}

#folders-list button {
  margin-left: 0 !important;
  margin-right: 0.5rem !important;
  margin-bottom: 0.5rem !important;
}

#action-selected-documents button,
#action-selected-documents span {
  margin-left: 0 !important;
  margin-right: 0.5rem !important;

  &:last-child {
    margin-right: 0 !important;
  }
}

#action-selected-documents {
  position: sticky;
  top: 72px;
  animation: slide-down 0.1s linear;
  z-index: calc(
    #{$zindex-sticky} - 1
  ); // to be under header dropdown menu (mobile)
  background: $light;
}

@include media-breakpoint-up(sm) {
  #action-selected-documents {
    top: 56px;
  }
}

#documents-count {
  position: relative;
  top: 0.5em;
}

.stop-spin {
  animation: unspin 0.5s 1 ease-out;
}

#document-drop-label {
  font-size: 1.2em;
  color: map_get($theme-colors, "light-gray");
  img {
    width: 200px;
    filter: drop-shadow(0 0 1px rgba(0, 0, 0, 0.2));
  }
}

#documents-sort {
  float: right;
  margin-right: 0 !important;

  ::v-deep .btn {
    padding-right: 0 !important;
    border-right: none !important;
  }
}

.documents-list-dragged-hover {
  background: adjust_color(map_get($theme-colors, "active"), $alpha: -0.7);
  ::v-deep * {
    pointer-events: none;
  }
  ::v-deep .card {
    opacity: 0.3;
  }
}
</style>
