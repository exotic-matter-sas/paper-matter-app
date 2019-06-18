<template>
  <b-col sm="2" class="m-1 folder">
    <b-row align-h="center">
      <span @click="$emit('event-navigate-folder', folder.id)"><b>{{ folder.name }}</b></span>
    </b-row>
    <b-row align-h="center">
      {{ folder.created }}
    </b-row>
    <b-row align-h="center">
      <b-button class="m-1" variant="secondary" @click="showModalMoveFolder">Move</b-button>
      <b-button class="m-1" variant="danger" @click="showModalDeleteFolder">Delete</b-button>
    </b-row>

    <b-modal id="move-folder"
             v-model="modalMoveFolder"
             :ok-disabled="!selectedFolder"
             @ok="moveFolder">
      <template slot="modal-title">
        <span v-if="selectedFolder">{{ this.$_('Move %s to %s', [folder.name, selectedFolder.name])}}</span>
        <span v-else>{{ this.$_('Move %s to ...', [folder.name])}}</span>
      </template>
      <b-container fluid>
        <span v-if="selectedFolder">{{this.$_('Selected folder: %s', [selectedFolder.name])}}</span>
        <span v-else>{{this.$_('No folder selected')}}</span>
        <FTLTreeFolders :root="isRoot"/>
      </b-container>
    </b-modal>
  </b-col>
</template>

<script>
  import FTLTreeFolders from "@/components/FTLTreeFolders";
  import axios from 'axios';
  import {axiosConfig} from "@/constants";

  export default {
    name: "FTLOrganizeFolder",
    components: {
      FTLTreeFolders
    },
    props: {
      folder: {
        type: Object,
        required: true
      }
    },

    data() {
      return {
        // Move folder
        modalMoveFolder: false
      }
    },

    computed: {
      selectedFolder: function () {
        return this.$store.state.selectedFolder
      },

      isRoot: function () {
        return this.folder.parent === null;
      }
    },

    methods: {
      showModalMoveFolder: function () {
        this.modalMoveFolder = true;
      },

      moveFolder: function () {
        const vi = this;
        let body = {
          parent: this.selectedFolder.id
        };

        axios
          .patch('/app/api/v1/folders/' + this.folder.id, body, axiosConfig)
          .then(response => {
            vi.$emit('event-move-folder', vi.selectedFolder.id);
            vi.$store.commit('selectFolder', null);
          })
          .catch(error => {
            vi.mixinAlert("Could not move folder", true)
          });
      },

      showModalDeleteFolder: function () {
        const vi = this;

        this.$bvModal.msgBoxConfirm(
          this.$_('Please confirm that you want to delete the folder and everything inside. This action is not reversible.'), {
            title: this.$_('Deletion of folders and its contents'),
            size: 'md',
            buttonSize: 'md',
            okVariant: 'danger',
            okTitle: this.$_('Yes, I want to delete the folder and everything inside'),
            cancelTitle: this.$_('No, cancel'),
            footerClass: 'm-1',
            hideHeaderClose: false,
            centered: true
          }).then(value => {
          if (value === true) {
            axios.delete('/app/api/v1/folders/' + vi.folder.id, axiosConfig)
              .then(response => {
                vi.$emit("event-delete-folder", vi.folder.id);
              }).catch(error => vi.mixinAlert("Unable to delete folder", true));
          }
        })
          .catch(err => {
            // TODO??
          });
      }
    }
  }
</script>

<style scoped>
.folder {
  cursor: pointer;
}
</style>
