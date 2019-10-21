<template>
  <main id="folders-mngt" class="flex-grow">
    <b-container fluid class="p-3 text-center">
      <b-row align-h="center">
        <!-- Left panel -->
        <b-col id="left-panel" md="8">
          <b-row>
            <b-col>
              <b-breadcrumb :items="breadcrumb"/>
            </b-col>
          </b-row>
          <b-row v-if="foldersLoading">
            <b-col>
              <b-spinner style="width: 3rem; height: 3rem;" class="m-5 loader"
                         label="Loading..."></b-spinner>
            </b-col>
          </b-row>
          <b-row align-h="center" v-else>
            <FTLSelectableFolder v-for="folder in folders" :key="folder.id" :folder="folder"
                                 @event-navigate-folder="navigateToFolder"
                                 @event-select-folder="getFolderDetail"
                                 @event-unselect-folder="unselectFolder"
            />
            <b-col
              id="create-folder"
              sm="2"
              class="m-1"
              v-b-modal="'modal-new-folder'">
              <b-row>
                <b-col>
                  <font-awesome-icon icon="folder-plus" size="5x" class="text-primary w-100"/>
                </b-col>
              </b-row>
              <b-row>
                <b-col><b>{{ this.$_('Create new folder') }}</b></b-col>
              </b-row>
            </b-col>
          </b-row>
        </b-col>
        <!-- Right panel -->
        <b-col id="right-panel">
          <b-row v-if="folderDetailLoading">
            <b-col>
              <b-spinner :label="$_('Loading')"></b-spinner>
            </b-col>
          </b-row>
          <b-row v-else-if="folderDetail">
            <b-col>
              <b-row>
                <b-col>
                  <font-awesome-icon icon="folder" size="6x"/>
                </b-col>
              </b-row>
              <b-row>
                <b-col id="selected-folder-name"><h1> {{ folderDetail.name }}</h1></b-col>
              </b-row>
              <b-row>
                <b-col>
                  Creation date
                </b-col>
                <b-col>
                  <span id="selected-folder-date" :title="folderDetail.created">{{ $moment(folderDetail.created).fromNow() }}</span>
                </b-col>
              </b-row>
              <b-row>
                <b-col>
                  <b-button id="rename-selected-folder" class="m-1" variant="secondary" v-b-modal="'modal-rename-folder'">Rename</b-button>
                  <b-button id="move-selected-folder" class="m-1" variant="secondary" v-b-modal="'modal-move-folder'">Move</b-button>
                  <b-button id="delete-selected-folder" class="m-1" variant="danger" v-b-modal="'modal-delete-folder'">Delete</b-button>
                </b-col>
              </b-row>
            </b-col>
          </b-row>
          <b-row v-else>
            <b-col><h1 class="text-muted">{{ this.$_('No folder selected') }}</h1></b-col>
          </b-row>
        </b-col>
      </b-row>

      <FTLRenameFolder
        v-if="folderDetail"
        :folder="folderDetail"
        @event-folder-renamed="refreshFolder"/>

      <FTLNewFolder
        :parent="getCurrentFolder"
        @event-folder-created="refreshFolder"/>

      <FTLDeleteFolder
        v-if="folderDetail"
        :folder="folderDetail"
        @event-folder-deleted="folderDeleted"/>

      <FTLMoveFolder
        v-if="folderDetail"
        :folder="folderDetail"
        @event-folder-moved="folderDeleted"/>
    </b-container>
  </main>
</template>

<script>
  import FTLSelectableFolder from "@/components/FTLSelectableFolder";
  import FTLNewFolder from "@/components/FTLNewFolder";
  import FTLRenameFolder from "@/components/FTLRenameFolder";
  import FTLDeleteFolder from "@/components/FTLDeleteFolder";
  import axios from 'axios';
  import FTLMoveFolder from "@/components/FTLMoveFolder";

  export default {
    name: 'Folders',
    components: {
      FTLMoveFolder,
      FTLDeleteFolder,
      FTLRenameFolder,
      FTLSelectableFolder,
      FTLNewFolder
    },
    props: ['folder'],

    data() {
      return {
        // Folders list
        foldersLoading: false,
        folders: [],

        // breadcrumb
        previousLevels: [],

        // Folder panel
        folderDetail: null,
        folderDetailLoading: false
      }
    },

    watch: {
      folder: function (newVal, oldVal) {
        if (newVal === undefined) {
          this.previousLevels = [];
          this.updateFolders();
        } else {
          if (newVal !== oldVal) {
            // Restore breadcrumb
            this.updateFoldersFromUrl(newVal);
          }
        }
      }
    },

    mounted() {
      if (this.folder) {
        this.updateFoldersFromUrl(this.folder);
      } else {
        this.updateFolders();
      }
    },

    computed: {
      getCurrentFolder: function () {
        if (this.previousLevels.length) {
          return this.previousLevels[this.previousLevels.length - 1];
        } else {
          return null;
        }
      },
      breadcrumb: function () {
        let paths = [];

        paths.push({
          text: this.$_('Root'),
          to: {name: 'folders'}
        });

        return paths.concat(this.previousLevels.map((e) => {
          return {
            text: e.name,
            to: {
              name: 'folders', params: {folder: e.id}
            }
          }
        }));
      }
    },

    methods: {
      refreshFolder: function () {
        this.unselectFolder();

        if (this.folder) {
          this.updateFoldersFromUrl(this.folder);
        } else {
          this.previousLevels = [];
          this.updateFolders();
        }
      },

      getFolderDetail: function (folder) {
        if (!this.folderDetail || this.folderDetail.id !== folder.id) {
          this.folderDetailLoading = true;
          // Avoid duplicate request to folder detail api because when doubleclicking, it also triggers single click event
          axios
            .get("/app/api/v1/folders/" + folder.id)
            .then(response => {
              this.folderDetail = response.data;
            })
            .catch(error => this.mixinAlert(this.$_('Unable to get folder details'), true))
            .finally(() => {
            })
            .then(() => this.folderDetailLoading = false);
        }
      },

      unselectFolder: function () {
        this.folderDetail = null;
      },

      navigateToFolder: function (folder) {
        if (folder) this.previousLevels.push(folder);
        this.$router.push({name: 'folders', params: {folder: folder.id}});
      },

      updateFolders: function (folder = null) {
        const vi = this;
        let qs = '';

        vi.foldersLoading = true;

        if (folder) {
          qs = '?level=' + folder.id;
        }

        axios
          .get("/app/api/v1/folders" + qs)
          .then(response => {
            vi.folders = response.data;
            vi.unselectFolder();
          })
          .catch(error => vi.mixinAlert(vi.$_('Unable to refresh folders list'), true))
          .finally(() => vi.foldersLoading = false);
      },

      updateFoldersFromUrl: function (folderId) {
        this.foldersLoading = true;

        if (this.folderDetail && this.folderDetail.id === folderId) {
          // Avoid duplicate request to folder detail api if we have already the detail because we clicked on the folder
          this.previousLevels = this.folderDetail.paths;
          this.updateFolders(this.folderDetail);
        } else {
          axios
            .get('/app/api/v1/folders/' + folderId)
            .then(response => {
              this.previousLevels = response.data.paths;
              this.updateFolders(response.data);
            })
            .catch(() => {
              this.mixinAlert("Could not open this folder", true);
              this.foldersLoading = false
            });
        }
      },

      folderDeleted: function (event) {
        const folder = event.folder;
        const foundIndex = this.folders.findIndex(x => x.id === folder.id);
        this.folders.splice(foundIndex, 1);

        this.unselectFolder();
      },

      folderUpdated: function (event) {
        const folder = event.folder;
        const foundIndex = this.folders.findIndex(x => x.id === folder.id);
        this.folders[foundIndex] = folder;
      }
    }
  }
</script>

<style scoped lang="scss">
  @import '../styles/customBootstrap.scss';

  #create-folder {
    cursor: pointer;
    border: 3px solid transparent;
  }

  #right-panel{
    border-top: 2px solid map_get($theme-colors, 'light-gray');
    margin-top: 1em;
    padding-top: 1em;
  }

  @include media-breakpoint-up(md) {
    #right-panel{
      border-top: 0;
      border-left: 2px solid map_get($theme-colors, 'light-gray');
      margin-top: 0;
      padding-top: 0;
    }
  }
</style>
