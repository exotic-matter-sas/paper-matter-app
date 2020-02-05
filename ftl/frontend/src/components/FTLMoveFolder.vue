<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <b-modal id="modal-move-folder"
           :ok-disabled="!selectedMoveTargetFolder"
           :cancel-title="$t('Cancel')"
           @ok="moveFolder">
    <template slot="modal-title">
          <span v-if="selectedMoveTargetFolder">
            {{ $t('Move "{0}" to "{1}"', [folder.name, selectedMoveTargetFolder.name])}}
          </span>
      <span v-else>{{ $t('Move "{0}" to...', [folder.name])}}</span>
    </template>
    <b-container fluid>
      <b-row>
        <b-col>
          <span
            v-if="selectedMoveTargetFolder">{{ $t('Selected folder: {0}', [selectedMoveTargetFolder.name])}}</span>
          <span v-else>{{ $t('No folder selected')}}</span>
          <FTLTreeFolders :root="isRoot" :source-folder="folder.id"/>
        </b-col>
      </b-row>
    </b-container>
  </b-modal>
</template>

<i18n>
  fr:
    Move "{0}" to "{1}": Déplacer « {0} » vers « {1} »
    Move "{0}" to...: Déplacer « {0} » vers ...
    "Selected folder: {0}": "Dossier sélectionné : {0}"
    No folder selected: Aucun dossier sélectionné
    Could not move folder: Le dossier n'a pu être déplacé
</i18n>

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
            this.mixinAlert(this.$t('Could not move folder'), true)
          });
      }
    }
  }
</script>

<style scoped>
</style>
