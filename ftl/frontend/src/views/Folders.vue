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
            <b-col>{{ this.$_('No folder. Why not create some?') }}</b-col>
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
                  <b-button class="m-1" variant="secondary" @click="showModalMoveFolder">Move</b-button>
                  <b-button class="m-1" variant="danger" @click="showModalDeleteFolder">Delete</b-button>
                </b-col>
              </b-row>
            </b-col>
          </b-row>
          <b-row v-else align-h="center">
            <b-col><h1>No folder selected</h1></b-col>
          </b-row>
        </b-col>
      </b-row>

      <b-modal id="move-folder"
               v-if="modalMoveFolder && folderDetail"
               v-model="modalMoveFolder"
               :ok-disabled="!selectedMoveTargetFolder"
               @ok="moveFolder">
        <template slot="modal-title">
          <span v-if="selectedMoveTargetFolder">
            {{ this.$_('Move %s to %s', [folderDetail.name, selectedMoveTargetFolder.name])}}
          </span>
          <span v-else>{{ this.$_('Move %s to ...', [folderDetail.name])}}</span>
        </template>
        <b-container fluid>
          <span v-if="selectedMoveTargetFolder">{{this.$_('Selected folder: %s', [folderDetail.name])}}</span>
          <span v-else>{{this.$_('No folder selected')}}</span>
          <FTLTreeFolders :root="isRoot" :sourceFolder="folderDetail.id"/>
        </b-container>
      </b-modal>
    </b-container>
  </section>
</template>

<script>
  import FTLOrganizeFolder from "@/components/FTLOrganizeFolder";
  import FTLTreeFolders from "@/components/FTLTreeFolders";
  import axios from 'axios';
  import {axiosConfig} from "@/constants";

  export default {
    name: 'Folders',
    components: {
      FTLOrganizeFolder, FTLTreeFolders
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

        // Move folder
        modalMoveFolder: false
      }
    },

    watch: {
      folder: function (newVal, oldVal) {
        if (newVal === undefined) {
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
      selectedMoveTargetFolder: function () {
        return this.$store.state.selectedMoveTargetFolder;
      },
      isRoot: function () {
        return this.folderDetail.parent === null;
      },
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
      },

      showModalMoveFolder: function () {
        this.modalMoveFolder = true;
      },

      moveFolder: function () {
        const vi = this;
        let body = {
          parent: this.selectedMoveTargetFolder.id
        };

        axios
          .patch('/app/api/v1/folders/' + this.folderDetail.id, body, axiosConfig)
          .then(response => {
            vi.$emit('event-move-folder', vi.selectedMoveTargetFolder.id);
            vi.$store.commit('selectMoveTargetFolder', null);
            vi.refreshFolder();
          })
          .catch(error => {
            vi.mixinAlert(vi.$_('Could not move folder'), true)
          });
      },

      showModalDeleteFolder: function () {
        const vi = this;

        this.$bvModal.msgBoxConfirm(
          this.$_('Please confirm that you want to delete the folder and everything inside. This action is not reversible.'), {
            title: this.$_('Deletion of folders and its contents'),
            size: 'md',
            buttonSize: 'md',
            okVariant: 'danger',
            okTitle: this.$_('Yes, I want to delete the folder and everything inside'),
            cancelTitle: this.$_('No, cancel'),
            footerClass: 'm-1',
            hideHeaderClose: false,
            centered: true
          }).then(value => {
          if (value === true) {
            axios
              .delete('/app/api/v1/folders/' + vi.folderDetail.id, axiosConfig)
              .then(response => {
                vi.$emit("event-delete-folder", vi.folderDetail.id);
                vi.refreshFolder();
              })
              .catch(error => vi.mixinAlert(vi.$_('Unable to delete folder'), true));
          }
        })
          .catch(err => {
            // TODO??
          });
      }
    }
  }
</script>

<style scoped>

</style>
