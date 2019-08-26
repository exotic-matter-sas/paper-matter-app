<template>
  <b-modal id="modal-rename-document"
           :ok-disabled="!newDocumentName || newDocumentName === doc.title"
           @ok="renameDocument">
    <template slot="modal-title">
      <span>Rename document</span>
    </template>
    <b-container fluid>
      <b-form-group
        id="fieldset-rename-document"
        :description="this.$_('The new name of the document')"
        :label="this.$_('The folder will be renamed to %s.', [newDocumentName])"
        label-for="rename-document-text">
        <b-form-input id="rename-document-text" autofocus v-model="newDocumentName" trim></b-form-input>
      </b-form-group>
    </b-container>
  </b-modal>
</template>

<script>
  import axios from "axios";
  import {axiosConfig} from "@/constants";

  export default {
    name: 'FTLRenameDocument',

    props: {
      doc: {
        Object,
        required: true
      }
    },

    data() {
      return {
        newDocumentName: this.doc.title,
      }
    },

    methods: {
      renameDocument: function () {
        let body = {title: this.newDocumentName};

        axios
          .patch('/app/api/v1/documents/' + this.doc.pid, body, axiosConfig)
          .then(response => {
            this.$emit('event-document-renamed', response.data);
            this.mixinAlert('Document successfully renamed');
          })
          .catch(error => {
            this.mixinAlert('Could not rename document', true);
          })
      }
    }
  }
</script>

<style>

</style>
