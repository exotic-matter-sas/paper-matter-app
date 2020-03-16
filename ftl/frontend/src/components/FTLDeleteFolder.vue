<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <b-modal id="modal-delete-folder"
           @ok="deleteFolder"
           :ok-disabled="deleting || name !== folder.name"
           :cancel-title="$t('Cancel')"
           ok-variant="danger">
    <span slot="modal-title">{{ $t('Deletion of folder "{0}" and its contents', [this.folder.name]) }}</span>
    <b-container>
      <b-form-group
        id="fieldset-delete-folder"
        :description="$t('Type the name of the folder to validate.')"
        :label="$t('Please confirm that you want to delete the folder and everything inside. This action is not reversible.')"
        label-for="delete-folder">
        <b-form-input id="delete-folder" autofocus v-model="name" trim></b-form-input>
      </b-form-group>
    </b-container>

    <template slot="modal-ok">
      <b-spinner :class="{'d-none': !deleting}" small></b-spinner>
      <font-awesome-icon :class="{'d-none': deleting }" icon="trash" :alt="this.$t('Delete')"/>
    </template>
  </b-modal>
</template>

<i18n>
  fr:
    Deletion of folder "{0}" and its contents: Suppression du dossier « {0} » et de son contenu
    Type the name of the folder to validate.: Saisissez le nom du dossier pour valider.
    Please confirm that you want to delete the folder and everything inside. This action is not reversible.: Veuillez
      confirmer que vous voulez supprimer le dossier et tout ce qu'il contient. Cette action est irréversible.
    Unable to delete folder: Le dossier n'a pu être supprimé
</i18n>

<script>
  import axios from "axios";
  import {axiosConfig} from "@/constants";

  export default {
    name: 'FTLDeleteFolder',
    props: {
      folder: {
        type: Object,
        required: true
      }
    },

    data() {
      return {
        name: '',
        deleting: false
      }
    },

    methods: {
      deleteFolder: function (bvModalEvt) {
        const vi = this;
        bvModalEvt.preventDefault();

        this.deleting = true;

        axios
          .delete('/app/api/v1/folders/' + this.folder.id, axiosConfig)
          .then(response => {
            this.$emit("event-folder-deleted", {'folder': this.folder});
            this.$nextTick(() => {
              vi.$bvModal.hide("modal-delete-folder");
            })
          })
          .catch(error => this.mixinAlert(this.$t('Unable to delete folder'), true))
          .then(() => {
            this.deleting = false
          })
      }
    }
  }
</script>

<style scoped>
</style>
