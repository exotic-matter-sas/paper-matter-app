<template>
  <main class="flex-grow">
    <b-col>
      <b-row class="my-3">
        <b-col>
          <FTLUpload :currentFolder="getCurrentFolder" @event-new-upload="documentsCreated"/>
        </b-col>
      </b-row>

      <b-row class="my-3" id="breadcrumb" no-gutter>
        <b-col>
          <b-breadcrumb class="m-0" :items="breadcrumb"/>
        </b-col>
      </b-row>

      <b-row v-show="!documentsSelected.length" class="my-3" id="folders-list">
        <b-col>
          <b-button id="refresh-documents" :disabled="docsLoading" variant="primary" @click="refreshAll">
            <font-awesome-icon icon="sync" :spin="docsLoading" :class="{ 'stop-spin':!docsLoading }"
                               :title="$_('Refresh documents list')"/>
          </b-button>
          <b-button id="create-folder" variant="primary" v-b-modal="'modal-new-folder'">
            <font-awesome-icon icon="folder-plus" :title="$_('Create new folder')"/>
          </b-button>
          <b-button variant="primary" :disabled="!previousLevels.length"
                    @click="changeToPreviousFolder">
            <font-awesome-icon icon="level-up-alt"/>
          </b-button>
          <FTLFolder v-for="folder in folders" :key="folder.id" :folder="folder"
                     @event-change-folder="navigateToFolder"/>
        </b-col>
      </b-row>

      <b-row v-show="documentsSelected.length" id="action-selected-documents">
        <b-col>
          <b-button id="select-all-documents" variant="outline-primary" title="Select all documents displayed"
                    @click="$store.commit('selectDocuments', docs)">
            {{ $_('Select all') }}
          </b-button>
        </b-col>
        <b-col cols="8" class="text-right">
          <span class="text-muted d-none d-sm-inline">{{ $_('%s documents:', [documentsSelected.length]) }}</span>
          <b-button id="move-documents" variant="primary" v-b-modal="'modal-move-documents'" title="Move to folder">
            <font-awesome-icon icon="folder-open" class="d-sm-none"/>
            <span class="d-none d-sm-inline">{{ $_('Move') }}</span>
          </b-button>
          <b-button id="delete-documents" variant="danger" v-b-modal="'modal-delete-documents'" title="Delete documents">
            <font-awesome-icon icon="trash" class="d-sm-none"/>
            <span class="d-none d-sm-inline">{{ $_('Delete') }}</span>
          </b-button>
          <b-button id="unselect-all-documents" @click="$store.commit('unselectAllDocuments')" title="Unselect documents">
            <font-awesome-icon icon="window-close" class="d-sm-none"/>
            <span class="d-none d-sm-inline">{{ $_('Cancel') }}</span>
          </b-button>
        </b-col>
      </b-row>

      <b-row class="my-3" id="documents-list">
        <b-col v-if="docsLoading">
          <b-spinner class="mx-auto" id="documents-list-loader"
                     label="Loading..."></b-spinner>
        </b-col>
        <b-col v-else-if="docs.length">
          <b-row tag="section">
            <FTLDocument v-for="doc in docs" :key="doc.pid" :doc="doc" @event-delete-doc="documentDeleted"
                         @event-open-doc="navigateToDocument"/>
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
      <b-modal id="document-viewer"
               hide-footer
               centered
               @hidden="closeDocument">
        <template slot="modal-header">
          <b-container>
            <b-row align-v="center">
              <b-col>
                <h5 class="d-inline modal-title">{{ currentOpenDoc.title }}</h5>
                <b-button id="rename-document" v-b-modal="'modal-rename-document'" variant="link">
                  <font-awesome-icon icon="edit" :title="$_('Rename document')"/>
                </b-button>
              </b-col>
              <b-col>
                <button @click="$bvModal.hide('document-viewer')" type="button" aria-label="Close" class="close">×</button>
              </b-col>
            </b-row>
          </b-container>
        </template>
        <b-container class="h-100">
          <b-row class="h-100">
            <b-col md="8">
              <div class="h-100 embed-responsive doc-pdf ">
                <iframe v-if="currentOpenDoc.pid" class="embed-responsive-item"
                        :src="`/assets/pdfjs/web/viewer.html?file=/app/uploads/` + currentOpenDoc.pid + `#search=` + currentSearch">
                </iframe>
              </div>
            </b-col>
            <b-col md="4" class="d-none d-md-block">
              <b-row>BBB</b-row>
              <b-row>CCC</b-row>
              <b-row>
                <b-col>
                  <b-button id="move-document" variant="secondary" v-b-modal="'modal-move-document'">Move</b-button>
                </b-col>
              </b-row>
            </b-col>
          </b-row>
        </b-container>
      </b-modal>

      <FTLNewFolder
        :parent="getCurrentFolder"
        @event-folder-created="folderCreated"/>

      <!-- For document panel Move button -->
      <FTLMoveDocuments
        v-if="currentOpenDoc"
        id="modal-move-document"
        :docs="[currentOpenDoc]"
        @event-document-moved="documentDeleted"/>

      <!-- For batch action move document -->
      <FTLMoveDocuments
        v-if="documentsSelected.length > 0"
        id="modal-move-documents"
        :docs="documentsSelected"
        @event-document-moved="documentDeleted"/>

      <FTLRenameDocument
        v-if="currentOpenDoc.pid"
        :doc="currentOpenDoc"
        @event-document-renamed="documentUpdated"/>

      <FTLDeleteDocuments
        v-if="documentsSelected.length > 0"
        :docs="documentsSelected"
        @event-document-deleted="documentDeleted"/>
    </b-col>
  </main>
</template>

<script>
  // @ is an alias to /src
  import FTLFolder from '@/components/FTLFolder.vue';
  import FTLDocument from '@/components/FTLDocument';
  import FTLUpload from '@/components/FTLUpload';
  import FTLNewFolder from "@/components/FTLNewFolder";
  import FTLDeleteDocuments from "@/components/FTLDeleteDocuments";
  import FTLThumbnailGenMixin from "@/components/FTLThumbnailGenMixin";
  import FTLMoveDocuments from "@/components/FTLMoveDocuments";
  import FTLRenameDocument from "@/components/FTLRenameDocument";
  import axios from 'axios';
  import qs from 'qs';

  export default {
    name: 'home',
    mixins: [FTLThumbnailGenMixin],

    components: {
      FTLDeleteDocuments,
      FTLMoveDocuments,
      FTLRenameDocument,
      FTLNewFolder,
      FTLFolder,
      FTLDocument,
      FTLUpload
    },

    props: ['searchQuery', 'doc', 'folder'],

    data() {
      return {
        // Documents list
        docs: [],
        docPid: null,
        docModal: false,
        lastRefresh: Date.now(),
        currentSearch: "",
        docsLoading: false,
        moreDocsLoading: false,
        moreDocs: null,

        // Folders list and breadcrumb
        folders: [],
        previousLevels: [],

        // PDF viewer
        currentOpenDoc: {},
        publicPath: process.env.BASE_URL
      }
    },

    mounted() {
      if (this.doc) {
        // Open document directly from loading an URL with document
        this.openDocument(this.doc);
      }

      if (this.folder) {
        // Open folder directly from loading an URL with folder (don't reset URL if opening a document)
        this.updateFoldersPath(this.folder);
      } else {
        // Or just show the current folders
        this.refreshFolders();

        if (this.searchQuery) {
          // search docs
          this.refreshDocumentWithSearch(this.searchQuery);
        } else {
          // all docs
          this.updateDocuments();
        }
      }
    },

    watch: {
      searchQuery: function (newVal, oldVal) {
        if (newVal !== oldVal) {
          this.refreshDocumentWithSearch(newVal);
        }
      },
      doc: function (newVal, oldVal) {
        if (newVal === undefined) {
          this.docModal = false;
        } else {
          if (newVal !== oldVal) {
            this.openDocument(newVal);
          }
        }
      },
      folder: function (newVal, oldVal) {
        if (this.$route.name === 'home') {
          // Coming back to home so clear everything and reload from root folder
          this.changeFolder();
        } else if (this.$route.name === 'home-folder') {
          // This is navigation between folders
          if (newVal !== oldVal) {
            this.updateFoldersPath(newVal, true);
          }
        } else if (this.$route.name === 'home-search') {
          // Do something? Nothing for now
        }

        // Clear the selected documents when moving between folders
        this.$store.commit("unselectAllDocuments");
      }
    },

    computed: {
      lastRefreshFormatted: function () {
        return new Date(this.lastRefresh);
      },

      getCurrentFolder: function () {
        if (this.previousLevels.length) {
          return this.previousLevels[this.previousLevels.length - 1];
        } else {
          return null;
        }
      },

      breadcrumb: function () {
        const vi = this;
        let paths = [];

        paths.push({
          text: this.$_('Root'),
          to: {name: 'home'}
        });

        return paths.concat(this.previousLevels.map((e) => {
          return {
            text: e.name,
            to: {
              path: '/home/' + vi.computeFolderUrlPath(e.id)
            }
          }
        }));
      },

      documentsSelected: function () {
        return this.$store.state.selectedDocumentsHome;
      }
    },

    methods: {
      computeFolderUrlPath: function (id = null) {
        if (this.previousLevels.length > 0) {
          let s = this.previousLevels.map(e => e.name);

          if (id) {
            s.push(id);
          } else {
            s.push(this.previousLevels[this.previousLevels.length - 1].id);
          }

          return s.join('/');
        } else {
          return '';
        }
      },

      refreshFolders: function () {
        this.updateFolders(this.getCurrentFolder);
      },

      refreshAll: function () {
        this.refreshFolders();
        this.updateDocuments();
      },

      changeFolder: function (folder = null) {
        this.currentSearch = "";
        if (folder === null) {
          this.previousLevels = [];
        }
        this.updateFolders(folder);
        this.updateDocuments();
      },

      navigateToFolder: function (folder) {
        if (folder) this.previousLevels.push(folder);
        this.currentSearch = "";
        this.$router.push({path: '/home/' + this.computeFolderUrlPath(folder.id)})
      },

      changeToPreviousFolder: function () {
        this.previousLevels.pop(); // Remove current level
        let level = this.getCurrentFolder;

        if (level === null) {
          this.$router.push({name: 'home'});
        } else {
          this.$router.push({path: '/home/' + this.computeFolderUrlPath(level.parent)})
        }
      },

      updateFoldersPath: function (folderId) {
        axios
          .get('/app/api/v1/folders/' + folderId)
          .then(response => {
            this.previousLevels = response.data.paths;
            this.changeFolder(response.data);
            // Allow refresh of the current URL in address bar to take into account folders paths changes
            if (this.docPid) {
              this.$router.push({
                path: '/home/' + this.computeFolderUrlPath(folderId),
                query: {
                  doc: this.docPid
                }
              });
            } else {
              this.$router.push({path: '/home/' + this.computeFolderUrlPath(folderId)});
            }
          })
          .catch(() => {
            this.mixinAlert("Could not open this folder", true);
          });
      },

      navigateToDocument: function (pid) {
        this.$router.push({query: {doc: pid}});
      },

      openDocument: function (pid) {
        const vi = this;

        this.docPid = pid;
        this.docModal = true;

        this.$bvModal.show('document-viewer');

        axios
          .get('/app/api/v1/documents/' + pid)
          .then(response => {
            vi.currentOpenDoc = response.data;

            if (!response.data.thumbnail_available) {
              vi.createThumbnailForDocument(response.data)
                .then(response => {
                  vi.mixinAlert("Thumbnail updated!");
                })
                .catch(error => vi.mixinAlert("Unable to create thumbnail", true));
            }
          })
          .catch(error => {
            vi.mixinAlert("Unable to show document.", true)
          });
      },

      closeDocument: function () {
        this.docModal = false;
        this.docPid = null;
        this.currentOpenDoc = {};
        this.$router.push({path: this.$route.path});
      },

      refreshDocumentWithSearch: function (text) {
        this.currentSearch = text;
        this.updateDocuments();
      },

      clearSearch: function () {
        this.refreshDocumentWithSearch("");
      },

      loadMoreDocuments: function () {
        const vi = this;
        this.moreDocsLoading = true;
        axios
          .get(this.moreDocs)
          .then(response => {
            this.moreDocsLoading = false;
            vi.docs = vi.docs.concat(response.data['results']);
            vi.moreDocs = response.data['next'];
            vi.lastRefresh = Date.now();
          }).catch(error => {
          this.moreDocsLoading = false;
          vi.mixinAlert("Unable to load more document.", true);
        });
      },

      updateDocuments: function () {
        let queryString = {};

        if (this.currentSearch !== null && this.currentSearch !== "") {
          queryString['search'] = this.currentSearch;
        } else {
          if (this.previousLevels.length > 0) {
            queryString['level'] = this.getCurrentFolder.id;
          }
        }

        let strQueryString = '?' + qs.stringify(queryString);

        this.docsLoading = true;

        axios
          .get('/app/api/v1/documents' + strQueryString)
          .then(response => {
            this.docsLoading = false;
            this.docs = response.data['results'];
            this.moreDocs = response.data['next'];
            this.lastRefresh = Date.now();
          }).catch(error => {
          this.docsLoading = false;
          this.mixinAlert("Unable to refresh documents list.", true);
        });
      },

      updateFolders: function (level = null) {
        const vi = this;
        let qs = '';

        // While loading folders, clear folders to avoid showing current sets of folders intermittently
        // vi.folders = [];

        if (level) {
          qs = '?level=' + level.id;
        }

        axios
          .get("/app/api/v1/folders" + qs)
          .then(response => {
            vi.folders = response.data;
          }).catch(error => vi.mixinAlert("Unable to refresh folders list", true));
      },

      folderCreated: function (folder) {
        this.refreshFolders();
      },

      documentsCreated: function (event) {
        const doc = event.doc;
        this.docs.unshift(doc);
      },

      documentDeleted: function (event) {
        const doc = event.doc;
        const foundIndex = this.docs.findIndex(x => x.pid === doc.pid);
        this.docs.splice(foundIndex, 1);
        // remove from selection
        this.$store.commit('unselectDocument', doc);
        // if last doc in the list has been removed and there is more docs to come, refresh list
        if (this.docs.length < 1 && this.moreDocs !== null){
            this.refreshDocumentWithSearch()
        }
      },

      documentUpdated: function (event) {
        const doc = event.doc;

        if (this.currentOpenDoc.pid === doc.pid) {
          this.currentOpenDoc = doc; // update open doc
        }

        const foundIndex = this.docs.findIndex(x => x.pid === doc.pid);
        this.docs[foundIndex] = doc; // update doc in the list
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

    &:last-child{
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
