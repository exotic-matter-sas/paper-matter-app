<!--
  - Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <b-modal :id="id"
           :ok-disabled="!selectedMoveTargetFolder"
           @ok="moveDocument">
    <template slot="modal-title">
      <span v-if="docs.length > 1">{{ this.$_('Move %s documents to ...', [docs.length])}}</span>
      <span v-else>{{ this.$_('Move %s to ...', [docs[0].title])}}</span>
    </template>
    <b-container fluid>
      <b-row>
        <b-col>
          <span
            v-if="selectedMoveTargetFolder">{{this.$_('Selected folder: %s', [selectedMoveTargetFolder.name])}}</span>
          <span v-else>{{this.$_('No folder selected')}}</span>
          <FTLTreeFolders :root="false"/>
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
              this.$emit('event-document-moved', {'doc': doc, 'target_folder': this.selectedMoveTargetFolder});
              this.$store.commit('selectMoveTargetFolder', null);
              this.mixinAlert('Document moved successfully');
            })
            .catch(error => {
              this.mixinAlert(this.$_('Could not move document'), true)
            });
        }
      }
    }
  }
</script>

<style scoped>
</style>
