<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the Business Source License. See LICENSE at project root for more information.
  -->

<template>
  <b-modal
    :id="modalId"
    :title="$tc('|Delete document|Delete documents', docs.length)"
    ok-variant="danger"
    :ok-title="$t('Delete')"
    :cancel-title="$t('Cancel')"
    @ok="deleteDocuments"
    auto-focus-button="ok"
  >
    <span v-if="docs.length > 1">{{
      $t("Please confirm that you want to delete {0} documents?", [docs.length])
    }}</span>
    <span v-else>{{
      $t('Please confirm that you want to delete "{0}".', [docs[0].title])
    }}</span>
  </b-modal>
</template>

<i18n>
  fr:
    "|Delete document|Delete documents": "|Supprimer le document|Supprimer les documents"
    Please confirm that you want to delete {0} documents?: Êtes-vous sûr de vouloir supprimer {0} documents ?
    Please confirm that you want to delete "{0}".: Veuillez confirmer la suppression de « {0} ».
    "| One document deleted successfully | {n} documents deleted successfully": "| Un document supprimé | {n} documents supprimés"
    "No document could be deleted | One document deleted successfully ({remain} couldn't) | {n} documents deleted successfully ({remain} couldn't)": "Aucun document n'a pu être supprimé | Un document supprimé ({remain} en erreur) | {n} documents supprimés ({remain} en erreur)"
    Could not delete document: Le document n'a pu être supprimé
</i18n>
<script>
import axios from "axios";
import { axiosConfig } from "@/constants";

export default {
  name: "FTLDeleteDocuments",

  props: {
    // customize the id to allow multiple time this component in Home
    // Used one time for batch delete document
    modalId: {
      type: String,
      default: "modal-delete-documents",
    },
    docs: {
      type: Array,
      required: true,
    },
  },

  data() {
    return {};
  },

  methods: {
    deleteDocuments: function () {
      const promisesDelete = [];
      const nb = this.docs.length; // store count due to async access later

      for (const doc of this.docs) {
        // store doc pid in axios config which will be available later in the response
        promisesDelete.push(
          axios.delete("/app/api/v1/documents/" + doc.pid, {
            ...axiosConfig,
            docPid: doc.pid,
          })
        );
      }

      Promise.allSettled(promisesDelete)
        .then((res) => res.filter((p) => p.status === "fulfilled"))
        .then((res) => res.map((p) => p.value))
        .then((res) => {
          for (const doc of res) {
            this.$emit("event-document-deleted", {
              doc: { pid: doc.config.docPid },
            });
          }

          if (res.length === nb) {
            this.mixinAlert(
              this.$tc(
                "| One document deleted successfully | {n} documents deleted successfully",
                res.length
              )
            );
          } else {
            this.mixinAlertWarning(
              this.$tc(
                "No document could be deleted | One document deleted successfully ({remain} couldn't) | {n} documents deleted successfully ({remain} couldn't)",
                res.length,
                { remain: nb - res.length }
              )
            );
          }
        });
    },
  },
};
</script>
