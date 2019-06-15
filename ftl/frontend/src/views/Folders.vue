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
                           @event-move-folder="refreshFolder"
                           @event-delete-folder="refreshFolder"/>
      </b-row>
      <b-row v-else>
        <b-col>{{ this.$_('No folder. Why not create some?') }}</b-col>
      </b-row>
    </b-container>
  </section>
</template>

<script>
  import FTLOrganizeFolder from "@/components/FTLOrganizeFolder";
  import axios from 'axios';

  export default {
    name: 'Folders',
    components: {
      FTLOrganizeFolder,
    },
    props: ['folder'],

    data() {
      return {
        // Folders list
        foldersLoading: false,
        folders: []
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
      this.updateFolders();
    },

    methods: {
      refreshFolder: function () {
        this.updateFolders(this.folder);
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
          }).catch(error => vi.mixinAlert("Unable to refresh folders list", true))
          .finally(() => vi.foldersLoading = false);
      }
    }
  }
</script>

<style scoped>

</style>
