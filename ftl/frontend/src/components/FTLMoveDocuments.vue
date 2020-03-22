<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <b-modal :id="id">
    <template slot="modal-title">
      <span>
        {{ $tc('| Move \"{documentTitle}\" to: | Move {n} documents to:', docs.length, {documentTitle: docs[0].title}) }}
      </span>
    </template>
    <b-container fluid>
      <b-row>
        <b-col>
          <FTLTreeFolders :folder-to-disable="folderToDisable"
                          :folder-to-disable-message="$t('current location')"/>
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
      <b-button variant="primary" @click.prevent="moveDocument" :disabled="!selectedMoveTargetFolder">
        {{ $t('OK') }}
      </b-button>
    </template>
  </b-modal>
</template>

<i18n>
  fr:
    "| Move \"{documentTitle}\" to: | Move {n} documents to:": "| Déplacer « {documentTitle} » vers : | Déplacer {n} documents vers :"
    "Selected folder: {0}": "Dossier sélectionné : {0}"
    current location: emplacement actuel
    No folder selected: Aucun dossier sélectionné
    Document moved successfully.: Le document a été déplacé avec succès.
    "No move needed. | One document moved successfully. | {n} documents moved successfully.": "Aucun déplacement nécessaire. | Un document déplacé. | {n} documents déplacés."
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
      folderToDisable: function () {
        // we only disable the source folder when one doc is selected (as several docs can have several sources)
        if (this.docs.length === 1) {
          return this.docs[0].ftl_folder;
        } else {
          return -1;
        }
      },
      ...mapState(['selectedMoveTargetFolder']) // generate vuex computed getter
    },

    methods: {
      moveDocument: function () {
        const promisesUpdate = [];
        let nb = this.docs.length; // store count due to async access later

        for (const doc of this.docs) {
          // If document is moved to its current location, nothing has to be done and no error is shown to user
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
              // nb could be equal to 0 due decrement which happen when folder is moved to its current location
              this.mixinAlert(this.$tc('No move needed. | One document moved successfully. | {n} documents moved successfully.',
                responses.length));
              this.$bvModal.hide(this.id)
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
  #selected-folder-label{
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    display: block;
  }
</style>
