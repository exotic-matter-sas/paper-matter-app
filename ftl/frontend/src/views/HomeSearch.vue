<template>
  <main class="flex-grow">
    <b-col>
      <b-row class="my-3">
        <b-col>
          <FTLUpload @event-new-upload="documentsCreated"/>
        </b-col>
      </b-row>

      <b-row v-show="!selectedDocumentsHome.length" class="my-3" id="folders-list">
        <b-col>
          <b-button id="refresh-documents" :disabled="docsLoading" variant="primary" @click="refreshAll">
            <font-awesome-icon icon="sync" :spin="docsLoading" :class="{ 'stop-spin':!docsLoading }"
                               :title="$_('Refresh documents list')"/>
          </b-button>

          <b-dropdown id="documents-sort" right variant="link" class="m-1 text-decoration-none">
            <template slot="button-content">
              <font-awesome-icon icon="sort"/>
              {{ $_('Sort') }}
              <span v-if="sort === 'az'">(a-z)</span>
              <span v-else-if="sort === 'za'">(z-a)</span>
              <span v-else-if="sort === 'recent'">({{ $_('recent') }})</span>
              <span v-else-if="sort === 'older'">({{ $_('older') }})</span>
              <span v-else-if="sort === 'relevance'">({{ $_('relevance') }})</span>
            </template>
            <b-dropdown-item-button id="az-sort" href="#" @click.prevent="sort = 'az'">{{ $_('A-Z') }}&nbsp;
              <span v-if="sort === 'az'">&checkmark;</span></b-dropdown-item-button>
            <b-dropdown-item-button id="za-sort" href="#" @click.prevent="sort = 'za'">{{ $_('Z-A') }}&nbsp;
              <span v-if="sort === 'za'">&checkmark;</span></b-dropdown-item-button>
            <b-dropdown-divider/>
            <b-dropdown-item-button id="recent-sort" href="#" @click.prevent="sort = 'recent'">{{ $_('Recent first') }}&nbsp;
              <span v-if="sort === 'recent'">&checkmark;</span></b-dropdown-item-button>
            <b-dropdown-item-button id="older-sort" href="#" @click.prevent="sort = 'older'">{{ $_('Older first') }}&nbsp;
              <span v-if="sort === 'older'">&checkmark;</span></b-dropdown-item-button>
            <b-dropdown-item-button id="relevance-sort" href="#" @click.prevent="sort = 'relevance'">{{ $_('Relevance')
              }}&nbsp;
              <span v-if="sort === 'relevance'">&checkmark;</span></b-dropdown-item-button>
          </b-dropdown>
        </b-col>
      </b-row>

      <b-row v-show="selectedDocumentsHome.length" id="action-selected-documents">
        <b-col>
          <b-button id="select-all-documents" variant="outline-primary" title="Select all documents displayed"
                    @click="$store.commit('selectDocuments', docs)">
            {{ $_('Select all') }}
          </b-button>
        </b-col>
        <b-col cols="8" class="text-right">
          <span class="text-muted d-none d-sm-inline">{{ $_('%s documents:', [selectedDocumentsHome.length]) }}</span>
          <b-button id="move-documents" variant="primary" v-b-modal="'modal-move-documents'" title="Move to folder">
            <font-awesome-icon icon="folder-open" class="d-sm-none"/>
            <span class="d-none d-sm-inline">{{ $_('Move') }}</span>
          </b-button>
          <b-button id="delete-documents" variant="danger" v-b-modal="'modal-delete-documents'"
                    title="Delete documents">
            <font-awesome-icon icon="trash" class="d-sm-none"/>
            <span class="d-none d-sm-inline">{{ $_('Delete') }}</span>
          </b-button>
          <b-button id="unselect-all-documents" @click="$store.commit('unselectAllDocuments')"
                    title="Unselect documents">
            <font-awesome-icon icon="window-close" class="d-sm-none"/>
            <span class="d-none d-sm-inline">{{ $_('Cancel') }}</span>
          </b-button>
        </b-col>
      </b-row>

      <b-row class="my-3" id="documents-list">
        <b-col v-if="docsLoading">
          <b-spinner class="mx-auto loader" id="documents-list-loader"
                     label="Loading..."></b-spinner>
        </b-col>
        <b-col v-else-if="docs.length">
          <b-row tag="section">
            <FTLDocument v-for="doc in docs" :key="doc.pid" :doc="doc" @event-open-doc="navigateToDocument"/>
          </b-row>
        </b-col>
        <b-col v-else class="text-center">{{ this.$_('No document yet') }}</b-col>
      </b-row>

      <b-row v-if="moreDocs" align-h="center" class="my-3">
        <b-col>
          <b-button id="more-documents" block variant="secondary" @click.prevent="loadMoreDocuments">
            <b-spinner class="loader" :class="{'d-none': !moreDocsLoading}" small></b-spinner>
            <span :class="{'d-none': moreDocsLoading}">{{ this.$_('Load more') }}</span>
          </b-button>
        </b-col>
      </b-row>

      <!-- Pdf viewer popup -->
      <FTLDocumentPanel v-if="docPid" :pid="docPid"
                        @event-document-panel-closed="closeDocument"
                        @event-document-renamed="documentUpdated"
                        @event-document-moved="documentDeleted"/>

      <!-- For batch action move document -->
      <FTLMoveDocuments
        v-if="selectedDocumentsHome.length > 0"
        id="modal-move-documents"
        :docs="selectedDocumentsHome"
        @event-document-moved="documentDeleted"/>

      <FTLRenameDocument
        v-if="currentOpenDoc.pid"
        :doc="currentOpenDoc"
        @event-document-renamed="documentUpdated"/>

      <FTLDeleteDocuments
        v-if="selectedDocumentsHome.length > 0"
        :docs="selectedDocumentsHome"
        @event-document-deleted="documentDeleted"/>
    </b-col>
  </main>
</template>

<script>
  // @ is an alias to /src
  import {mapState} from 'vuex'
  import HomeBase from "@/views/HomeBase";
  import FTLDocumentPanel from "@/components/FTLDocumentPanel";
  import FTLDeleteDocuments from "@/components/FTLDeleteDocuments";
  import FTLMoveDocuments from "@/components/FTLMoveDocuments";
  import FTLDocument from "@/components/FTLDocument";
  import FTLUpload from "@/components/FTLUpload";
  import FTLRenameDocument from "@/components/FTLRenameDocument";

  export default {
    name: 'home-search',
    extends: HomeBase,

    components: {
      FTLDocumentPanel,
      FTLDeleteDocuments,
      FTLMoveDocuments,
      FTLDocument,
      FTLUpload,
      FTLRenameDocument
    },

    props: ['searchQuery', 'doc'],

    data() {
      return {
        // Documents list
        currentSearch: "",
        sort: "relevance"
      }
    },

    mounted() {
      if (this.searchQuery) {
        // search docs
        this.refreshDocumentWithSearch(this.searchQuery);
      } else {
        // all docs
        this.updateDocuments();
      }
    },

    watch: {
      searchQuery: function (newVal, oldVal) {
        if (newVal !== oldVal) {
          this.refreshDocumentWithSearch(newVal);
        }
      }
    },

    computed: {
      ...mapState(['selectedDocumentsHome']) // generate vuex computed getter
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
          queryString['search'] = this.currentSearch;
        }

        return this._updateDocuments(queryString);
      }
    }
  }
</script>

<style scoped lang="scss">
  @import '../styles/customBootstrap.scss';

  #documents-list-loader {
    width: 3em;
    height: 3em;
    display: block;
  }

  #folders-list button, #action-selected-documents button, #action-selected-documents span {
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
    z-index: calc(#{$zindex-sticky} - 1); // to be under header dropdown menu (mobile)
    background: $light;
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
    margin-top: -0.5rem;
    margin-bottom: -0.5rem;
  }

  @include media-breakpoint-up(sm) {
    #action-selected-documents {
      top: 56px;
    }
  }

  .stop-spin {
    animation: unspin 0.5s 1 ease-out;
  }
</style>

<style lang="scss">
  @import '../styles/customBootstrap.scss';

  #documents-sort {
    float: right;
    margin-right: 0 !important;

    .btn {
      padding-right: 0 !important;
      border-right: none !important;
    }
  }
</style>
