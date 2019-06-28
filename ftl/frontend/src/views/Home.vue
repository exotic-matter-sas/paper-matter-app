<template>
  <div>
    <section>
      <b-container>
        <b-row>
          <b-col>
            <FTLUpload :currentFolder="getCurrentFolder" @event-new-upload="updateDocuments"/>
          </b-col>
        </b-row>
        <b-row>
          <b-col>
            <b-button id="generate-thumb" variant="primary" class="m-1" @click="generateMissingThumbnail">
              {{this.$_('Generate missing thumb')}}
            </b-button>
            {{ this.$_('Last refresh') }} {{ lastRefreshFormatted }}
          </b-col>
        </b-row>
      </b-container>
    </section>

    <section>
      <b-container>
        <b-row>
          <b-col class="p-0">
            <b-breadcrumb class="m-0" :items="breadcrumb"/>
          </b-col>
        </b-row>
      </b-container>
      <b-container>
        <b-row>
          <b-col>
            <div class="d-flex flex-wrap align-items-center">
              <b-button id="refresh-documents" :disabled="docLoading" variant="primary" class="m-1" @click="refreshAll">
                <font-awesome-icon icon="sync" :spin="docLoading" :title="$_('Refresh documents list')"/>
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
            </div>
          </b-col>
        </b-row>
      </b-container>
    </section>

    <section id="documents-list">
      <b-container>
        <b-row v-if="docLoading">
          <b-col>
            <b-spinner id="documents-list-loader" style="width: 3rem; height: 3rem;" class="m-5"
                       label="Loading..."></b-spinner>
          </b-col>
        </b-row>
        <b-row align-h="around" v-else-if="docs.length">
          <FTLDocument v-for="doc in docs" :key="doc.pid" :doc="doc" @event-delete-doc="updateDocuments"
                       @event-open-doc="openDocument"/>
        </b-row>
        <b-row v-else>
          <b-col>{{ this.$_('No document yet') }}</b-col>
        </b-row>
      </b-container>
    </section>


    <!-- Pdf viewer popup -->
    <div v-if="docModal" class="doc-view-modal" :class="{open: docModal}">
      <b-container>
        <b-row>
          <b-col md="10">
            <span id="document-title">{{ this.$_('Title:') }} {{ currentOpenDoc.title }}</span>
          </b-col>
          <b-col>
            <b-button id="close-document" variant="secondary" @click="closeDocument">{{this.$_('Close')}}</b-button>
          </b-col>
        </b-row>

      </b-container>
      <b-container>
        <b-row scr>
          <b-col md="8">
            <div class="embed-responsive embed-responsive-1by1 doc-pdf ">
              <iframe v-if="currentOpenDoc.pid" class="embed-responsive-item"
                      :src="`/assets/pdfjs/web/viewer.html?file=/app/uploads/` + currentOpenDoc.pid + `#search=` + currentSearch">
              </iframe>
            </div>
          </b-col>
          <b-col>
            <b-row>AAA</b-row>
            <b-row>BBB</b-row>
            <b-row>CCC</b-row>
          </b-col>
        </b-row>
      </b-container>
      <b-container>
        <b-row align-h="end">
          <b-col cols="2">
            <b-button variant="secondary" @click="closeDocument">{{this.$_('Close')}}</b-button>
          </b-col>
        </b-row>
      </b-container>
    </div>

    <FTLNewFolder
      :parent="getCurrentFolder"
      @event-folder-created="folderCreated"/>
  </div>
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
        docLoading: false,

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
    },

    watch: {
      searchQuery: function (newVal, oldVal) {
        this.refreshDocumentWithSearch(newVal);
      },
      doc: function (newVal, oldVal) {
        if (newVal === undefined) {
          this.docModal = false;
        } else {
          this.openDocument(newVal);
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

      openDocument: function (pid) {
        const vi = this;

        this.docPid = pid;
        this.docModal = true;

        axios
          .get('/app/api/v1/documents/' + pid)
          .then(response => {
            vi.currentOpenDoc = response.data;

            if (!response.data.thumbnail_available) {
              vi.createThumbnailForDocument(response.data);
            }
            vi.$router.push({path: '/home/' + vi.computeFolderUrlPath(), query: {doc: pid}});
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

      updateDocuments: function () {
        let queryString = {};

        if (this.previousLevels.length > 0) {
          queryString['level'] = this.getCurrentFolder.id;
        }

        if (this.currentSearch !== null && this.currentSearch !== "") {
          queryString['search'] = this.currentSearch;
        }

        let strQueryString = '?' + qs.stringify(queryString);

        this.docLoading = true;

        axios
          .get('/app/api/v1/documents/' + strQueryString)
          .then(response => {
            this.docLoading = false;
            this.docs = response.data['results'];
            this.lastRefresh = Date.now();
          }).catch(error => {
          this.docLoading = false;
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

<style scoped>
  /* PDF.js viewer custom css */
  .doc-view-modal {
    display: none;
    height: 100%;
    left: 0;
    position: fixed;
    top: 0;
    width: 100%;
    background: white;
    z-index: 1000;
    padding: 20px;
  }

  .doc-view-modal {
    display: flex;
    flex-direction: column;
  }

  .doc-pdf {
    padding-top: 100%;
  }
</style>
