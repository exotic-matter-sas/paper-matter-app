<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <b-modal :id="id"
           :ok-disabled="!selectedMoveTargetFolder"
           :cancel-title="$t('Cancel')"
           @ok="moveDocument">
    <template slot="modal-title">
      <span v-if="docs.length > 1">{{ $t('Move {0} documents to...', [docs.length])}}</span>
      <span v-else>{{ $t('Move {0} to...', [docs[0].title])}}</span>
    </template>
    <b-container fluid>
      <b-row>
        <b-col>
          <span
            v-if="selectedMoveTargetFolder">{{ $t('Selected folder: {0}', [selectedMoveTargetFolder.name] )}}</span>
          <span v-else>{{$t('No folder selected')}}</span>
          <FTLTreeFolders :root="false"/>
        </b-col>
      </b-row>
    </b-container>
  </b-modal>
</template>

<i18n>
  fr:
    Move {0} documents to...: Déplacer {0} documents vers ...
    Move {0} to...: Déplacer {0} vers ...
    "Selected folder: {0}": "Dossier sélectionné: {0}"
    No folder selected: Aucun dossier sélectionné
    Could not move document: Le document n'a pu être déplacé
</i18n>

<script>
  import FTLTreeFolders from "@/components/FTLTreeFolders";
  import axios from "axios";
  import {axiosConfig} from "@/constants";
  import {mapState} from "vuex";

  export default {
    name: 'FTLMoveDocuments',

    components: {FTLTreeFolders},

    props: {
      // customize the id to allow multiple time this component in Home
      // Used one time for document panel move button
      // Used one time for batch move document
      id: {
        type: String,
        default: "modal-move-documents"
      },
      docs: {
        type: Array,
        required: true
      }
    },

    data() {
      return {}
    },

    computed: {
      ...mapState(['selectedMoveTargetFolder']) // generate vuex computed getter
    },

    methods: {
      moveDocument: function () {
        for (const doc of this.docs) {
          if (doc.ftl_folder === this.selectedMoveTargetFolder.id) {
            continue;
          }

          let body = {
            ftl_folder: this.selectedMoveTargetFolder.id
          };

          axios
            .patch('/app/api/v1/documents/' + doc.pid, body, axiosConfig)
            .then(response => {
              this.$emit('event-document-moved', {
                'doc': response.data,
                'target_folder': this.selectedMoveTargetFolder
              });
              this.$store.commit('selectMoveTargetFolder', null);
              this.mixinAlert('Document moved successfully');
            })
            .catch(error => {
              this.mixinAlert(this.$t('Could not move document'), true)
            });
        }
      }
    }
  }
</script>

<style scoped>
</style>
