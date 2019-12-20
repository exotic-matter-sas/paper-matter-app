<!--
  - Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

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
      <b-row>
        <b-col>
          <span
            v-if="selectedMoveTargetFolder">{{this.$_('Selected folder: %s', [selectedMoveTargetFolder.name])}}</span>
          <span v-else>{{this.$_('No folder selected')}}</span>
          <FTLTreeFolders :root="isRoot" :source-folder="folder.id"/>
        </b-col>
      </b-row>
    </b-container>
  </b-modal>
</template>

<script>
  import FTLTreeFolders from "@/components/FTLTreeFolders";
  import axios from "axios";
  import {axiosConfig} from "@/constants";
  import {mapState} from "vuex";

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
      isRoot: function () {
        return this.folder.parent === null;
      },
      ...mapState(['selectedMoveTargetFolder']) // generate vuex computed getter
    },

    methods: {
      moveFolder: function () {
        let body = {
          parent: this.selectedMoveTargetFolder.id
        };

        axios
          .patch('/app/api/v1/folders/' + this.folder.id, body, axiosConfig)
          .then(response => {
            this.$emit('event-folder-moved', {'folder': this.folder, 'target_folder': this.selectedMoveTargetFolder});
            this.$store.commit('selectMoveTargetFolder', null);
          })
          .catch(error => {
            this.mixinAlert(this.$_('Could not move folder'), true)
          });
      }
    }
  }
</script>

<style scoped>
</style>
