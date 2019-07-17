<template>
  <main>
    <b-col>
      <b-row class="my-3">
        <FTLUpload class="col" :currentFolder="getCurrentFolder" @event-new-upload="updateDocuments"/>
      </b-row>
      <!-- <b-row class="my-3" id="toolbar">
        <b-button id="generate-thumb" variant="primary" class="mt-2 mr-0 mt-sm-0 mr-sm-2" @click="generateMissingThumbnail">
          {{this.$_('Generate missing thumb')}}
        </b-button>
      </b-row> -->

      <b-row class="my-3" id="breadcrumb">
        <b-breadcrumb class="m-0" :items="breadcrumb"/>
      </b-row>

      <b-row class="my-3" id="folders-list">
        <b-button id="refresh-documents" :disabled="docsLoading" variant="primary" class="m-1" @click="refreshAll">
          <font-awesome-icon icon="sync" spin :class="{ 'stop-spin':!docsLoading }" :title="$_('Refresh documents list')"/>
        </b-button>
        <b-button id="create-folder" class="m-1" variant="primary" v-b-modal="'modal-new-folder'">
          <font-awesome-icon icon="folder-plus" :title="$_('Create new folder')"/>
        </b-button>
        <b-button variant="primary" class="m-1" :disabled="!previousLevels.length"
                        @click="changeToPreviousFolder">
          <font-awesome-icon icon="level-up-alt"/>
        </b-button>
        <FTLFolder v-for="folder in folders" :key="folder.id" :folder="folder"
                   @event-change-folder="navigateToFolder"/>
      </b-row>

      <b-row class="my-3" id="documents-list">
        <b-col v-if="docsLoading">
          <b-spinner class="mx-auto" id="documents-list-loader"
                     label="Loading..."></b-spinner>
        </b-col>
        <b-col v-else-if="docs.length">
          <section class="row">
            <FTLDocument v-for="doc in docs" :key="doc.pid" :doc="doc" @event-delete-doc="updateDocuments"
                         @event-open-doc="navigateToDocument"/>
          </section>
        </b-col>
        <b-col v-else class="text-center">{{ this.$_('No document yet') }}</b-col>
      </b-row>

      <b-row v-if="moreDocs" align-h="center" class="my-3">
        <b-button id="more-documents" block variant="secondary" @click.prevent="loadMoreDocuments">
          <b-spinner class="loader" :class="{'d-none': !moreDocsLoading}" small></b-spinner>
          <span :class="{'d-none': moreDocsLoading}">{{ this.$_('Load more') }}</span>
        </b-button>
      </b-row>

      <!-- Pdf viewer popup -->
      <b-modal id="document-viewer"
               :title="currentOpenDoc.title"
               hide-footer
               centered>
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
              <b-row>AAA</b-row>
              <b-row>BBB</b-row>
              <b-row>CCC</b-row>
            </b-col>
          </b-row>
        </b-container>
      </b-modal>

    <FTLNewFolder
      :parent="getCurrentFolder"
      @event-folder-created="folderCreated"/>
    </b-col>
  </main>
</template>

<script>
  // @ is an alias to /src
  import FTLFolder from '@/components/FTLFolder.vue';
  import FTLDocument from '@/components/FTLDocument';
  import FTLUpload from '@/components/FTLUpload';
  import FTLNewFolder from "@/components/FTLNewFolder";
  import axios from 'axios';
  import qs from 'qs';
  import {createThumbFromUrl} from "@/thumbnailGenerator";
  import {axiosConfig} from "@/constants";

  export default {
    name: 'home',
    components: {
      FTLNewFolder,
      FTLFolder,
      FTLDocument,
      FTLUpload
    },

    props: ['searchQuery', 'doc', 'paths', 'folder'],

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
      }

      if (this.searchQuery) {
        // search docs
        this.refreshDocumentWithSearch(this.searchQuery);
      } else {
        // all docs
        this.updateDocuments();
      }

      // Listen to modal event
      this.$root.$on('bv::modal::hide', (bvEvent, modalId) => {
        if (modalId === 'document-viewer') {
          this.closeDocument()
        }
      })
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
        // Detect navigation in folders
        if (newVal === undefined) {
          // Root folder
          this.changeFolder()
        } else {
          if (newVal !== oldVal) {
            this.updateFoldersPath(newVal, true);
          }
        }
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
        this.$router.push({path: '/home/' + this.computeFolderUrlPath(), query: {doc: pid}});
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
              vi.createThumbnailForDocument(response.data);
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
        this.$router.push({path: '/home/' + this.computeFolderUrlPath()});
      },

      createThumbnailForDocument: async function (doc, updateDocuments = true) {
        const vi = this;
        let thumb64;

        try {
          thumb64 = await createThumbFromUrl('/app/uploads/' + doc.pid);
        } catch (e) {
          vi.mixinAlert("Unable to update thumbnail", true);
          return;
        }

        let jsonData = {'thumbnail_binary': thumb64};

        axios.patch('/app/api/v1/documents/' + doc.pid, jsonData, axiosConfig)
          .then(response => {
            vi.mixinAlert("Thumbnail updated!");
            if (updateDocuments) {
              vi.updateDocuments();
            }
          }).catch(error => vi.mixinAlert("Unable to update thumbnail", true));
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

        if (this.previousLevels.length > 0) {
          queryString['level'] = this.getCurrentFolder.id;
        }

        if (this.currentSearch !== null && this.currentSearch !== "") {
          queryString['search'] = this.currentSearch;
        }

        let strQueryString = '?' + qs.stringify(queryString);

        this.docsLoading = true;

        axios
          .get('/app/api/v1/documents/' + strQueryString)
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
          .get("/app/api/v1/folders/" + qs)
          .then(response => {
            vi.folders = response.data;
          }).catch(error => vi.mixinAlert("Unable to refresh folders list", true));
      },

      folderCreated: function (folder) {
        this.refreshFolders();
      },

      generateMissingThumbnail: function () {
        const vi = this;
        vi.mixinAlert("Updating thumbnail");

        axios.get("/app/api/v1/documents?flat=true")
          .then(async response => {
            let documents = response.data;

            while (documents !== null && documents.results.length > 0) {
              for (const doc of documents.results) {
                if (doc['thumbnail_available'] === false) {
                  await vi.createThumbnailForDocument(doc, false);
                }
              }

              if (documents.next == null) {
                documents = null;
              } else {
                let resp = await axios.get(documents.next);
                documents = await resp.data;
              }
            }
          })
          .catch(error => {
            vi.mixinAlert("An error occurred while updating thumbnail", true)
          })
          .then(() => {
            vi.mixinAlert("Finished updating thumbnail");
          });
      }
    }
  }
</script>

<style scoped lang="scss">
  @import '../styles/customBootstrap.scss';

  #documents-list-loader{
    width: 3em;
    height: 3em;
    display: block;
  }

  #folders-list, #breadcrumb{
    padding: 0 15px;
  }

  #folders-list button, #folders-list button{
    margin-left: 0 !important;
    margin-right: 0.5rem !important;
  }

  .stop-spin{
    animation: unspin 0.5s 1 ease-out;
  }

  @keyframes unspin {
    to {
      transform: rotate(-0.5turn);
    }
  }
</style>
