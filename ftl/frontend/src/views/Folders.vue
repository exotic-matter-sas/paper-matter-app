<template>
  <section id="folders-mngt">
    <h1>Organize your folders</h1>

    <b-container fluid>
      <b-row>
        <b-col md="8">
          <b-row v-if="foldersLoading">
            <b-col>
              <b-spinner style="width: 3rem; height: 3rem;" class="m-5"
                         label="Loading..."></b-spinner>
            </b-col>
          </b-row>
          <b-row align-h="center" v-else-if="folders.length">
            <FTLOrganizeFolder v-for="folder in folders" :key="folder.id" :folder="folder"
                               @event-navigate-folder="updateFolders"
                               @event-select-folder="getFolderDetail"
                               @event-unselect-folder="unselectFolder"/>
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
          this.updateFolders(newVal);
        }
      }
    },

    mounted() {
      if (this.folder) {
        this.updateFolders(this.folder);
      }
    },

    computed: {
      selectedMoveTargetFolder: function () {
        return this.$store.state.selectedMoveTargetFolder;
      },
      isRoot: function () {
        return this.folderDetail.parent === null;
      }
    },

    methods: {
      refreshFolder: function () {
        this.updateFolders(this.folder);
        this.unselectFolder();
      },

      getFolderDetail: function (id) {
        const vi = this;

        axios
          .get("/app/api/v1/folders/" + id)
          .then(response => {
            vi.folderDetail = response.data;
          })
          .catch(error => vi.mixinAlert(vi.$_('Unable to refresh folders list'), true))
          .finally(() => {
          });
      },

      unselectFolder: function () {
        this.folderDetail = null;
      },

      updateFolders: function (level = null) {
        const vi = this;
        let qs = '';

        vi.foldersLoading = true;

        // While loading folders, clear folders to avoid showing current sets of folders intermittently
        // vi.folders = [];

        if (level) {
          qs = '?level=' + level;
        }

        axios
          .get("/app/api/v1/folders/" + qs)
          .then(response => {
            vi.folders = response.data;
            if (level) {
              vi.$router.push({name: 'folders', params: {folder: level}});
            }
            vi.unselectFolder();
          })
          .catch(error => vi.mixinAlert(vi.$_('Unable to refresh folders list'), true))
          .finally(() => vi.foldersLoading = false);
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
