<template>
  <section id="folders-mngt">
    <h1>Organize your folders</h1>

    <b-container fluid>
      <b-row v-if="foldersLoading">
        <b-col>
          <b-spinner style="width: 3rem; height: 3rem;" class="m-5"
                     label="Loading..."></b-spinner>
        </b-col>
      </b-row>
      <b-row align-h="center" v-else-if="folders.length">
        <FTLOrganizeFolder v-for="folder in folders" :key="folder.id" :folder="folder"
                           @event-navigate-folder="updateFolders"
                           @event-delete-folder="deleteFolder"/>
      </b-row>
      <b-row v-else>
        <b-col>{{ this.$_('No folder. Why not create some?') }}</b-col>
      </b-row>
    </b-container>

    <b-container>
      Selected folder {{selectedFolder}}
      <FTLTreeFolders/>
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
      FTLTreeFolders,
      FTLOrganizeFolder,
    },
    props: ['folder'],

    data() {
      return {
        // Folders list
        foldersLoading: false,
        folders: [],
      }
    },

    watch: {
      folder: function (newVal, oldVal) {
        if (newVal === undefined) {
          this.updateFolders();
        } else {
          this.updateFolders({id: newVal});
        }
      }
    },

    computed: {
      selectedFolder: function () {
        return this.$store.state.selectedFolder
      }
    },

    mounted() {
      this.updateFolders();
    },

    methods: {
      deleteFolder: function (folder) {
        const vi = this;

        this.$bvModal.msgBoxConfirm(this.$_('Please confirm that you want to delete the folder and everything inside. This action is not reversible.'), {
          title: this.$_('Deletion of folders and its contents'),
          size: 'md',
          buttonSize: 'md',
          okVariant: 'danger',
          okTitle: this.$_('Yes, I want to delete the folder and everything inside'),
          cancelTitle: this.$_('No, cancel'),
          footerClass: 'm-1',
          hideHeaderClose: false,
          centered: true
        })
          .then(value => {
            if (value === true) {
              axios.delete('/app/api/v1/folders/' + folder.id, axiosConfig)
                .then(response => {
                  this.$router.go(-1);
                }).catch(error => vi.mixinAlert("Unable to delete folder", true));
            }
          })
          .catch(err => {
            // TODO
          });
      },

      updateFolders: function (level = null) {
        const vi = this;
        let qs = '';

        vi.foldersLoading = true;

        // While loading folders, clear folders to avoid showing current sets of folders intermittently
        vi.folders = [];

        if (level) {
          qs = '?level=' + level.id;
        }

        axios
          .get("/app/api/v1/folders/" + qs)
          .then(response => {
            vi.folders = response.data;
            if (level) {
              vi.$router.push({name: 'folders', params: {folder: level.id}});
            }
          }).catch(error => vi.mixinAlert("Unable to refresh folders list", true))
          .finally(() => vi.foldersLoading = false);
      }
    }
  }
</script>

<style scoped>

</style>
