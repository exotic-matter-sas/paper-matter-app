<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <b-modal
    id="modal-new-folder"
    @ok="createNewFolder"
    :ok-disabled="newFolderName === ''"
    :cancel-title="$t('Cancel')"
    :ok-title="$t('Create')"
  >
    <span slot="modal-title">{{ $t("Create a new folder") }}</span>
    <b-container>
      <b-form-group
        id="fieldset-new-folder"
        :description="
          $t('The folder will be created in \'{0}\' folder.', [
            this.getParentName,
          ])
        "
        :label="$t('Name of the folder')"
        label-for="new-folder"
      >
        <b-form-input
          id="new-folder"
          autofocus
          v-model="newFolderName"
          trim
          @keyup.enter="newFolderName && createNewFolder($event)"
        ></b-form-input>
      </b-form-group>
    </b-container>
  </b-modal>
</template>

<i18n>
  fr:
    Create a new folder: Créer un nouveau dossier
    The folder will be created in '{0}' folder.: Le dossier sera créé dans « {0} ».
    Name of the folder: Nom du dossier
    Folder "{0}" created: Dossier « {0} » créé avec succès
    Unable to create new folder: La création du dossier a échoué
</i18n>

<script>
import axios from "axios";
import { axiosConfig } from "@/constants";

export default {
  name: "FTLNewFolder",

  props: {
    parent: {
      type: Object,
      default: null,
    },
  },

  data() {
    return {
      newFolderName: "",
    };
  },

  computed: {
    getParentName: function () {
      if (this.parent == null) {
        return this.$t("Root");
      } else {
        return this.parent.name;
      }
    },
  },

  methods: {
    createNewFolder: function () {
      let postBody;
      if (this.parent) {
        postBody = { name: this.newFolderName, parent: this.parent.id };
      } else {
        postBody = { name: this.newFolderName };
      }

      axios
        .post("/app/api/v1/folders", postBody, axiosConfig)
        .then((response) => {
          this.mixinAlert(
            this.$t('Folder "{0}" created', [this.newFolderName])
          );
          this.newFolderName = "";
          this.$bvModal.hide("modal-new-folder");
          this.$emit("event-folder-created", response.data);
        })
        .catch((error) => {
          let error_details = null;
          try {
            error_details = error.response.data.details;
          } finally {
            this.mixinAlert(
              this.$t("Unable to create new folder"),
              true,
              error_details
            );
          }
        });
    },
  },
};
</script>

<style scoped></style>
