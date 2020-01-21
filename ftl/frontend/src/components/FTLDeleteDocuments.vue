<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <b-modal :id="id"
           :title="$t('Delete documents')"
           ok-variant="danger"
           :ok-title="$t('Delete')"
           :cancel-title="$t('Cancel')"
           @ok="deleteDocuments">
    <span v-if="docs.length > 1">{{ $t('Please confirm that you want to delete {0} documents?', [docs.length]) }}</span>
    <span v-else>{{ $t('Please confirm that you want to delete "{0}".', [docs[0].title])}}</span>
  </b-modal>
</template>

<i18n>
  fr:
    Delete documents: Supprimer les documents
    Please confirm that you want to delete {0} documents?: Êtes-vous sûr de vouloir supprimer {0} documents ?
    Please confirm that you want to delete "{0}".: Veuillez confirmer la suppression de « {0} ».
    "| One document deleted successfully. | {n} documents deleted successfully.": "| Un document supprimé. | {n} documents supprimés."
    Could not delete document: Le document n'a pu être supprimé
</i18n>
<script>
  import axios from "axios";
  import {axiosConfig} from "@/constants";

  export default {
    name: 'FTLDeleteDocuments',

    props: {
      // customize the id to allow multiple time this component in Home
      // Used one time for batch delete document
      // TODO next, in doc panel?
      id: {
        type: String,
        default: "modal-delete-documents"
      },
      docs: {
        type: Array,
        required: true
      }
    },

    data() {
      return {}
    },

    methods: {
      deleteDocuments: function () {
        let toasted = false;
        const nb = this.docs.length; // store count due to async access later

        for (const doc of this.docs) {
          axios
            .delete('/app/api/v1/documents/' + doc.pid, axiosConfig)
            .then((response) => {
              this.$emit('event-document-deleted', {'doc': doc})

              if (!toasted) {
                this.mixinAlert(
                  this.$tc('| One document deleted successfully. | {n} documents deleted successfully.', nb));
                toasted = true;
              }
            })
            .catch(error => this.mixinAlert(this.$t('Could not delete document'), true));
        }
      }
    }
  }
</script>

<style>

</style>
