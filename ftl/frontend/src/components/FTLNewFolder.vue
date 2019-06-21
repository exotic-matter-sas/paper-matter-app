<template>
  <b-modal v-model="showModal"
           @ok="createNewFolder"
           @hide="$emit('event-folder-cancel')"
           :ok-disabled="newFolderName === ''"
           :cancel-title="this.$_('Cancel')"
           :ok-title="this.$_('Create')">
    <span slot="modal-title">{{ this.$_('Create a new folder') }}</span>
    <b-container>
      <!-- TODO add current folder name to title -->
      <b-form-group
        id="fieldset-new-folder"
        :description="this.$_('The name of the folder')"
        :label="this.$_('The folder will be created in the current folder.')"
        label-for="new-folder">
        <b-form-input id="new-folder" v-model="newFolderName" trim></b-form-input>
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
      show: {
        type: Boolean,
        default: false
      },
      parent: {
        type: Object,
        default: null
      }
    },

    data() {
      return {
        showModal: false,
        newFolderName: '',
      }
    },

    watch: {
      show: function (newVal, oldVal) {
        // hack for avoid parent prop to show the popup again
        if (newVal === true) {
          this.showModal = true;
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
          }).catch(error => this.mixinAlert("Unable to create new folder.", true));
      }
    }
  }
</script>

<style scoped>
</style>
