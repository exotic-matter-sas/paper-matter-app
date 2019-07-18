<template>
  <b-modal id="modal-new-folder"
           @ok="createNewFolder"
           :ok-disabled="newFolderName === ''"
           :cancel-title="this.$_('Cancel')"
           :ok-title="this.$_('Create')">
    <span slot="modal-title">{{ this.$_('Create a new folder') }}</span>
    <b-container>
      <b-form-group
        id="fieldset-new-folder"
        :description='this.$_("The folder will be created in \"%s\" folder.", [this.getParentName])'
        :label="this.$_('Name of the folder')"
        label-for="new-folder">
        <b-form-input id="new-folder" autofocus v-model="newFolderName" trim></b-form-input>
      </b-form-group>
    </b-container>
  </b-modal>
</template>

<script>
  import axios from "axios";
  import {axiosConfig} from "@/constants";

  export default {
    name: 'FTLNewFolder',

    props: {
      parent: {
        type: Object,
        default: null
      }
    },

    data() {
      return {
        newFolderName: '',
      }
    },

    computed: {
      getParentName: function () {
        if (this.parent == null) {
          return this.$_('Root');
        } else {
          return this.parent.name;
        }
      }
    },

    methods: {
      createNewFolder: function () {
        let postBody;
        if (this.parent) {
          postBody = {name: this.newFolderName, parent: this.parent.id};
        } else {
          postBody = {name: this.newFolderName};
        }

        axios
          .post("/app/api/v1/folders/", postBody, axiosConfig)
          .then((response) => {
            // TODO flash the new folder when just created
            this.mixinAlert(this.$_("Folder %s created", [this.newFolderName]));
            this.newFolderName = '';
            this.$emit('event-folder-created', response.data);
          }).catch((error) => {
          let error_details = null;
          try {
            error_details = error.response.data.details;
          } finally {
            this.mixinAlert(this.$_('Unable to create new folder'), true, error_details);
          }
        });
      }
    }
  }
</script>

<style scoped>
</style>
