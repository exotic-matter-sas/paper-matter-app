<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <b-modal
    id="modal-rename-document"
    :ok-disabled="!newDocumentName || newDocumentName === doc.title"
    @ok="renameDocument"
  >
    <template slot="modal-title">
      <span>{{ $t("Rename document") }}</span>
    </template>
    <b-container fluid>
      <b-form-group
        id="fieldset-rename-document"
        :description="$t('The new name of the document')"
        :label="
          $t('The document will be renamed to \'{0}\'.', [newDocumentName])
        "
        label-for="rename-document-text"
        class="text-truncate"
      >
        <b-form-input
          id="rename-document-text"
          autofocus
          onfocus="this.select()"
          v-model="newDocumentName"
          trim
        ></b-form-input>
      </b-form-group>
    </b-container>
  </b-modal>
</template>

<i18n>
  fr:
    Rename document: Renommer le document
    The new name of the document: Le nouveau nom du document
    The document will be renamed to "{0}".: Le document sera renommé « {0} ».
    Document successfully renamed.: Le document a été renommé avec succès.
    Could not rename document.: Le document n'a pas pu être renommé.
</i18n>

<script>
import axios from "axios";
import { axiosConfig } from "@/constants";

export default {
  name: "FTLRenameDocument",

  props: {
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

  methods: {
    renameDocument: function () {
      let body = { title: this.newDocumentName };

      axios
        .patch("/app/api/v1/documents/" + this.doc.pid, body, axiosConfig)
        .then((response) => {
          this.$emit("event-document-renamed", {
            doc: response.data,
          });
          this.mixinAlert(this.$t("Document successfully renamed."));
        })
        .catch((error) => {
          this.mixinAlert(this.$t("Could not rename document."), true);
        });
    },
  },
};
</script>

<style></style>
