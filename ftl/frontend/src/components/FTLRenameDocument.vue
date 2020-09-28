<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <b-modal
    :id="modalId"
    :ok-disabled="!newDocumentName || newDocumentName === doc.title"
    @ok="renameDocument"
  >
    <template slot="modal-title">
      <span>{{ $t("Rename document") }}</span>
    </template>
    <b-container>
      <b-form-group
        id="fieldset-rename-document"
        :description="$t('The new name of the document')"
        :label="
          $t('The document will be renamed to \'{0}{1}\'.', [
            newDocumentName,
            doc.ext,
          ])
        "
        label-for="rename-document-text"
        label-class="text-truncate"
      >
        <b-form-input
          id="rename-document-text"
          autofocus
          onfocus="this.select()"
          v-model="newDocumentName"
          trim
          @keyup.enter="
            newDocumentName &&
              newDocumentName !== doc.title &&
              renameDocument($event)
          "
        ></b-form-input>
      </b-form-group>
    </b-container>
  </b-modal>
</template>

<i18n>
  fr:
    Rename document: Renommer le document
    The new name of the document: Le nouveau nom du document
    The document will be renamed to '{0}{1}'.: Le document sera renommé « {0}{1} ».
    Document successfully renamed: Le document a été renommé avec succès
    Could not rename document: Le document n'a pu être renommé
</i18n>

<script>
import axios from "axios";
import { axiosConfig } from "@/constants";

export default {
  name: "FTLRenameDocument",

  props: {
    // customize the id to allow multiple usage of this component at the same time
    modalId: {
      type: String,
      default: "modal-rename-document",
    },
    doc: {
      Object,
      required: true,
    },
  },

  data() {
    return {
      newDocumentName: this.doc.title,
    };
  },

  watch: {
    doc: function (newVal, oldVal) {
      if (newVal.pid !== oldVal.pid) {
        this.newDocumentName = newVal.title;
      }
    },
  },

  methods: {
    renameDocument: function () {
      let body = { title: this.newDocumentName };

      axios
        .patch("/app/api/v1/documents/" + this.doc.pid, body, axiosConfig)
        .then((response) => {
          this.$emit("event-document-renamed", {
            doc: response.data,
          });
          this.$bvModal.hide(this.modalId);
          this.mixinAlert(this.$t("Document successfully renamed"));
        })
        .catch((error) => {
          this.mixinAlert(this.$t("Could not rename document"), true);
        });
    },
  },
};
</script>
