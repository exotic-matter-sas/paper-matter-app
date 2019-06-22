<template>
  <b-modal id="modal-move-folder"
           :ok-disabled="!selectedMoveTargetFolder"
           @ok="moveFolder">
    <template slot="modal-title">
          <span v-if="selectedMoveTargetFolder">
            {{ this.$_('Move %s to %s', [folder.name, selectedMoveTargetFolder.name])}}
          </span>
      <span v-else>{{ this.$_('Move %s to ...', [folder.name])}}</span>
    </template>
    <b-container fluid>
      <span v-if="selectedMoveTargetFolder">{{this.$_('Selected folder: %s', [selectedMoveTargetFolder.name])}}</span>
      <span v-else>{{this.$_('No folder selected')}}</span>
      <FTLTreeFolders :root="isRoot" :sourceFolder="folder.id"/>
    </b-container>
  </b-modal>
</template>

<script>
  import FTLTreeFolders from "@/components/FTLTreeFolders";
  import axios from "axios";
  import {axiosConfig} from "@/constants";

  export default {
    name: 'FTLMoveFolder',
    components: {FTLTreeFolders},
    props: {
      folder: {
        type: Object,
        required: true
      }
    },

    data() {
      return {}
    },

    computed: {
      selectedMoveTargetFolder: function () {
        return this.$store.state.selectedMoveTargetFolder;
      },
      isRoot: function () {
        return this.folder.parent === null;
      },
    },

    methods: {
      moveFolder: function () {
        let body = {
          parent: this.selectedMoveTargetFolder.id
        };

        axios
          .patch('/app/api/v1/folders/' + this.folder.id, body, axiosConfig)
          .then(response => {
            this.$emit('event-folder-moved', this.selectedMoveTargetFolder);
            this.$store.commit('selectMoveTargetFolder', null);
          })
          .catch(error => {
            this.mixinAlert(vi.$_('Could not move folder'), true)
          });
      }
    }
  }
</script>

<style scoped>
</style>
