<template>
  <b-modal id="modal-move-document"
           :ok-disabled="!selectedMoveTargetFolder"
           @ok="moveDocument">
    <template slot="modal-title">
      <span>{{ this.$_('Move %s to ...', [doc.title])}}</span>
    </template>
    <b-container fluid>
      <b-row>
        <b-col>
          <span
            v-if="selectedMoveTargetFolder">{{this.$_('Selected folder: %s', [selectedMoveTargetFolder.name])}}</span>
          <span v-else>{{this.$_('No folder selected')}}</span>
          <FTLTreeFolders :root="isRoot" :source-folder="getFolder"/>
        </b-col>
      </b-row>
    </b-container>
  </b-modal>
</template>

<script>
  import FTLTreeFolders from "@/components/FTLTreeFolders";
  import axios from "axios";
  import {axiosConfig} from "@/constants";

  export default {
    name: 'FTLMoveDocument',

    components: {FTLTreeFolders},

    props: {
      doc: {
        type: Object,
        required: true
      }
    },

    data() {
      return {}
    },

    computed: {
      getFolder: function () {
        if (this.doc.ftl_folder === null) {
          return -1;
        } else {
          return this.doc.ftl_folder;
        }
      },
      selectedMoveTargetFolder: function () {
        return this.$store.state.selectedMoveTargetFolder;
      },
      isRoot: function () {
        return this.doc.ftl_folder === null;
      },
    },

    methods: {
      moveDocument: function () {
        let body = {
          ftl_folder: this.selectedMoveTargetFolder.id
        };

        axios
          .patch('/app/api/v1/documents/' + this.doc.pid, body, axiosConfig)
          .then(response => {
            this.$emit('event-document-moved', {'doc': this.doc, 'folder': this.selectedMoveTargetFolder});
            this.$store.commit('selectMoveTargetFolder', null);
            this.mixinAlert('Document moved successfully');
          })
          .catch(error => {
            this.mixinAlert(this.$_('Could not move document'), true)
          });
      }
    }
  }
</script>

<style scoped>
</style>
