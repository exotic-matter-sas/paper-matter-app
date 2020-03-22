<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <b-modal :id="id">
    <template slot="modal-title">
      <span v-if="selectedMoveTargetFolder">
        {{ $t('Move "{0}" to "{1}"', [folder.name, selectedMoveTargetFolder.name])}}
      </span>
      <span v-else>{{ $t('Move "{0}" to...', [folder.name])}}</span>
    </template>
    <b-container fluid>
      <b-row>
        <b-col>
          <FTLTreeFolders :folder-to-disable="folder.parent"
                          :folder-to-disable-message="$t('current location')"
                          :folder-to-hide="folder.id"/>
        </b-col>
      </b-row>
    </b-container>
    <template slot="modal-footer">
      <div id="selected-folder-label" class="flex-grow-1 text-muted text-left font-italic">
        <span v-if="selectedMoveTargetFolder" :title="selectedMoveTargetFolder.name">
          {{ $t('Selected folder: {0}', [selectedMoveTargetFolder.name] )}}
        </span>
        <span v-else>{{$t('No folder selected')}}</span>
      </div>
      <b-button variant="secondary" @click.prevent="$bvModal.hide(id)">
        {{ $t('Cancel') }}
      </b-button>
      <b-button variant="primary" @click.prevent="moveFolder" :disabled="!selectedMoveTargetFolder">
        {{ $t('OK') }}
      </b-button>
    </template>
  </b-modal>
</template>

<i18n>
  fr:
    Move "{0}" to "{1}": Déplacer « {0} » vers « {1} »
    Move "{0}" to...: Déplacer « {0} » vers ...
    current location: emplacement actuel
    "Selected folder: {0}": "Dossier sélectionné : {0}"
    No folder selected: Aucun dossier sélectionné
    Could not move folder: Le dossier n'a pu être déplacé
    Selected folder is already located in this folder.: Le dossier sélectionné est déjà dans ce dossier.
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
      return {
        id: 'modal-move-folder'
      }
    },

    computed: {
      ...mapState(['selectedMoveTargetFolder']) // generate vuex computed getter
    },

    methods: {
      moveFolder: function () {
        if(this.folder.parent === this.selectedMoveTargetFolder.id){
          this.mixinAlertWarning(this.$t('Selected folder is already located in this folder.'));
        } else {
          let body = {
            parent: this.selectedMoveTargetFolder.id
          };

          axios
            .patch('/app/api/v1/folders/' + this.folder.id, body, axiosConfig)
            .then(response => {
              this.$emit('event-folder-moved', {'folder': this.folder, 'target_folder': this.selectedMoveTargetFolder});
              this.$store.commit('selectMoveTargetFolder', null);
              this.$bvModal.hide(this.id)
            })
            .catch(error => {
              this.mixinAlert(this.$t('Could not move folder'), true)
            });
        }
      }
    }
  }
</script>

<style scoped>
  #selected-folder-label{
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    display: block;
  }
</style>
