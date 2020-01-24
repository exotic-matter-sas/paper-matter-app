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
      <span v-else>{{ $t('Move "{0}" to...', [docs[0].title])}}</span>
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
    Move "{0}" to...: Déplacer « {0} » vers ...
    "Selected folder: {0}": "Dossier sélectionné : {0}"
    No folder selected: Aucun dossier sélectionné
    Document moved successfully.: Le document a été déplacé avec succès.
    "| One document moved successfully. | {n} documents moved successfully.": "| Un document déplacé. | {n} documents déplacés."
    "No document could be moved. | One document moved successfully ({remain} couldn't). | {n} documents moved successfully ({remain} couldn't).": "Aucun document n'a pu être déplacé. | Un document déplacé ({remain} en erreur). | {n} documents déplacés ({remain} en erreur)."
    Could not move document.: Le document n'a pu être déplacé.
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
        const promisesUpdate = [];
        let nb = this.docs.length; // store count due to async access later

        for (const doc of this.docs) {
          if (doc.ftl_folder === this.selectedMoveTargetFolder.id) {
            --nb;
            continue;
          }

          let body = {
            ftl_folder: this.selectedMoveTargetFolder.id
          };

          promisesUpdate.push(axios
            .patch('/app/api/v1/documents/' + doc.pid, body, {...axiosConfig, docPid: doc.pid}));
        }

        console.log(promisesUpdate);

        Promise.allSettled(promisesUpdate)
          .then(res => res.filter(p => p.status === "fulfilled"))
          .then(res => res.map(p => p.value))
          .then(responses => {
            for (const res of responses) {
              this.$emit('event-document-moved', {
                'doc': res.data,
                'target_folder': this.selectedMoveTargetFolder
              });
            }

            this.$store.commit('selectMoveTargetFolder', null);

            if (responses.length === nb) {
              this.mixinAlert(this.$tc('| One document moved successfully. | {n} documents moved successfully.', responses.length))
            } else {
              this.mixinAlertWarning(
                this.$tc('No document could be moved. | One document moved successfully ({remain} couldn\'t). | {n} documents moved successfully ({remain} couldn\'t).',
                  responses.length, {remain: nb - responses.length}));
            }
          });
      }
    }
  }
</script>

<style scoped>
</style>
