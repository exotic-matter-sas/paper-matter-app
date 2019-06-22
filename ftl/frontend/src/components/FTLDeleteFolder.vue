<template>
  <b-modal id="modal-delete-folder"
           @ok="deleteFolder"
           :ok-disabled="name !== folder.name"
           :cancel-title="this.$_('Cancel')"
           :ok-title="this.$_('Delete')"
           ok-variant="danger">
    <span slot="modal-title">{{ this.$_('Deletion of folders and its contents') }}</span>
    <b-container>
      <b-form-group
        id="fieldset-delete-folder"
        :description="this.$_('Type the name of the folder to validate.')"
        :label="this.$_('Please confirm that you want to delete the folder and everything inside. This action is not reversible.')"
        label-for="delete-folder">
        <b-form-input id="delete-folder" v-model="name" trim></b-form-input>
      </b-form-group>
    </b-container>
  </b-modal>
</template>

<script>
  import axios from "axios";
  import {axiosConfig} from "@/constants";

  export default {
    name: 'FTLDeleteFolder',
    props: {
      folder: {
        type: Object,
        required: true
      }
    },

    data() {
      return {
        name: ''
      }
    },

    methods: {
      deleteFolder: function () {
        axios
          .delete('/app/api/v1/folders/' + this.folder.id, axiosConfig)
          .then(response => {
            this.$emit("event-folder-deleted", this.folder);
          })
          .catch(error => this.mixinAlert(this.$_('Unable to delete folder'), true));
      }
    }
  }
</script>

<style scoped>
</style>
