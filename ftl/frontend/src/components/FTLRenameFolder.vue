<template>
  <b-modal id="modal-rename-folder"
           :ok-disabled="!newFolderName"
           @ok="renameFolder">
    <template slot="modal-title">
      <span>Rename folder</span>
    </template>
    <b-container fluid>
      <b-form-group
        id="fieldset-rename-folder"
        :description="this.$_('The new name of the folder')"
        :label="this.$_('The folder will be renamed.')"
        label-for="rename-folder-text">
        <b-form-input id="rename-folder-text" autofocus onfocus="this.select()" v-model="newFolderName" trim></b-form-input>
      </b-form-group>
    </b-container>
  </b-modal>
</template>

<script>
  import axios from "axios";
  import {axiosConfig} from "@/constants";

  export default {
    name: 'FTLRenameFolder',
    props: {
      folder: {
        type: Object,
        required: true
      }
    },

    data() {
      return {
        newFolderName: this.folder.name,
      }
    },

    methods: {
      renameFolder: function () {
        let body = {name: this.newFolderName};

        axios
          .patch('/app/api/v1/folders/' + this.folder.id, body, axiosConfig)
          .then(response => {
            this.$emit('event-folder-renamed', response.data);
            this.mixinAlert('Folder successfully renamed');
          })
          .catch(error => {
            this.mixinAlert('Could not rename folder', true);
          })
      }
    }
  }
</script>

<style scoped>

</style>
