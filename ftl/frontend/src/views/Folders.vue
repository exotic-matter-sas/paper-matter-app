<template>
  <section id="folders-mngt">
    <h1>Organize your folders</h1>

    <b-container fluid>
      <b-row>
        <b-col md="8">
          <b-row>
            <b-col class="p-0">
              <b-breadcrumb class="m-0" :items="breadcrumb"/>
            </b-col>
          </b-row>
          <b-row v-if="foldersLoading">
            <b-col>
              <b-spinner style="width: 3rem; height: 3rem;" class="m-5"
                         label="Loading..."></b-spinner>
            </b-col>
          </b-row>
          <b-row align-h="center" v-else-if="folders.length">
            <FTLOrganizeFolder v-for="folder in folders" :key="folder.id" :folder="folder"
                               @event-navigate-folder="navigateToFolder"
                               @event-select-folder="getFolderDetail"
            />
          </b-row>
          <b-row v-else>
            <b-col>{{ this.$_('No folder. Why not create some?') }}<br/>
              <b-button id="create-folder" class="m-1" variant="outline-primary" size="sm"
                        v-b-modal="'modal-new-folder'">
                {{ this.$_('Create new folder') }}
              </b-button>
            </b-col>
          </b-row>
        </b-col>
        <b-col>
          <b-row v-if="folderDetail" align-h="center">
            <b-col>
              <b-row>
                <b-col>
                  <font-awesome-icon icon="folder" size="6x"/>
                </b-col>
              </b-row>
              <b-row>
                <b-col><h1> {{ folderDetail.name }}</h1></b-col>
              </b-row>
              <b-row>
                <b-col>
                  Creation date
                </b-col>
                <b-col>
                  <span :title="folderDetail.created">{{ $moment(folderDetail.created).fromNow() }}</span>
                </b-col>
              </b-row>
              <b-row>
                <b-col>
                  <b-button class="m-1" variant="secondary" v-b-modal="'modal-rename-folder'">Rename</b-button>
                  <b-button class="m-1" variant="secondary" v-b-modal="'modal-move-folder'">Move</b-button>
                  <b-button class="m-1" variant="danger" v-b-modal="'modal-delete-folder'">Delete</b-button>
                </b-col>
              </b-row>
            </b-col>
          </b-row>
          <b-row v-else align-h="center">
            <b-col><h1>No folder selected</h1></b-col>
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
        @event-folder-deleted="refreshFolder"/>

      <FTLMoveFolder
        v-if="folderDetail"
        :folder="folderDetail"
        @event-folder-moved="refreshFolder"/>
    </b-container>
  </section>
</template>

<script>
  import FTLOrganizeFolder from "@/components/FTLOrganizeFolder";
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
      FTLOrganizeFolder,
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
          text: 'Root',
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
          // Avoid duplicate request to folder detail api because when doubleclicking, it also triggers single click event
          axios
            .get("/app/api/v1/folders/" + folder.id)
            .then(response => {
              this.folderDetail = response.data;
            })
            .catch(error => this.mixinAlert(this.$_('Unable to refresh folders list'), true))
            .finally(() => {
            });
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
          .get("/app/api/v1/folders/" + qs)
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
      }
    }
  }
</script>

<style scoped>

</style>
