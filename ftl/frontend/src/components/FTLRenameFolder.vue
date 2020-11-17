<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the Business Source License. See LICENSE at project root for more information.
  -->

<template>
  <b-modal
    :id="modalId"
    :ok-disabled="!newFolderName"
    :cancel-title="$t('Cancel')"
    @ok="renameFolder"
  >
    <template slot="modal-title">
      <span>{{ $t("Rename folder") }}</span>
    </template>
    <b-container fluid>
      <b-form-group
        id="fieldset-rename-folder"
        :description="$t('The folder will be renamed.')"
        :label="$t('The new name of the folder')"
        label-for="rename-folder-text"
      >
        <b-form-input
          id="rename-folder-text"
          autofocus
          onfocus="this.select()"
          v-model="newFolderName"
          trim
          @keyup.enter="
            newFolderName &&
              newFolderName !== folder.name &&
              renameFolder($event)
          "
        ></b-form-input>
      </b-form-group>
    </b-container>
  </b-modal>
</template>

<i18n>
  fr:
    Rename folder: Renommer le dossier
    The new name of the folder: Le nouveau nom du dossier
    The folder will be renamed.: Le dossier sera renommé.
    Folder successfully renamed: Le dossier a été renommé avec succès
    Could not rename folder: Le dossier n'a pu être renommé
</i18n>

<script>
import axios from "axios";
import { axiosConfig } from "@/constants";

export default {
  name: "FTLRenameFolder",
  props: {
    modalId: {
      type: String,
      default: "modal-rename-folder",
    },
    folder: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      newFolderName: this.folder.name,
    };
  },

  methods: {
    renameFolder: function () {
      let body = { name: this.newFolderName };

      axios
        .patch("/app/api/v1/folders/" + this.folder.id, body, axiosConfig)
        .then((response) => {
          this.$bvModal.hide(this.modalId);
          this.$emit("event-folder-renamed", {
            folder: response.data,
          });
          this.mixinAlert(this.$t("Folder successfully renamed"));
        })
        .catch((error) => {
          this.mixinAlert(this.$t("Could not rename folder"), true);
        });
    },
  },
};
</script>
