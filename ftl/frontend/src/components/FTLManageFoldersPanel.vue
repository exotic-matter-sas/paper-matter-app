<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <b-modal
    id="modal-manage-folders"
    hide-footer
    centered
    scrollable
    body-class="px-0"
  >
    <!-- Header -->
    <template slot="modal-header">
      <b-container>
        <h5 class="modal-title">
          <span
            id="folder-parent"
            class="float-left text-primary"
          >
            <font-awesome-icon icon="folder" />
            <font-awesome-icon icon="folder-open" class="d-none" />
            {{ parentFolder === null ? $t('Root') : parentFolder.name }}
          </span>
          <div id="title-separator" class="float-left">
            >
          </div>
          <div
            id="title"
            class="float-left"
          >
            <span>{{ $t('Folders management') }}</span>
          </div>
        </h5>

        <button
          @click.prevent="$bvModal.hide('modal-manage-folders')"
          type="button"
          aria-label="Close"
          class="close"
        >
          ×
        </button>
      </b-container>
    </template>
    <b-container fluid class="text-center">
      <b-row>
        <!-- Left panel -->
        <b-col id="left-panel" md="8">
          <b-row align-h="center">
            <b-col
              id="create-folder"
              sm="2"
              class="m-1"
              v-b-modal="'modal-new-folder-mfp'"
            >
              <b-row>
                <b-col>
                  <font-awesome-icon
                    icon="folder-plus"
                    size="5x"
                    class="text-primary w-100"
                  />
                </b-col>
              </b-row>
              <b-row>
                <b-col
                ><b>{{ $t("Add") }}</b></b-col
                >
              </b-row>
            </b-col>
            <FTLSelectableFolder
              v-for="_folder in childrenFolders"
              :key="_folder.id"
              :folder="_folder"
              @event-select-folder="getFolderDetails"
              @event-unselect-folder="unselectFolder"
            />
          </b-row>
        </b-col>
        <!-- Right panel -->
        <b-col id="right-panel">
          <b-row v-if="folderDetailLoading" class="sticky-top">
            <b-col>
              <b-spinner :label="$t('Loading')"></b-spinner>
            </b-col>
          </b-row>
          <b-row v-else-if="folderDetail" class="sticky-top">
            <b-col>
              <b-row>
                <b-col>
                  <font-awesome-icon icon="folder" size="6x" />
                </b-col>
              </b-row>
              <b-row>
                <b-col id="selected-folder-name"
                ><h1>{{ folderDetail.name }}</h1></b-col
                >
              </b-row>
              <b-row>
                <b-col>
                  {{ $t("Creation date") }}
                </b-col>
                <b-col>
                <span
                  id="selected-folder-date"
                  :title="folderDetail.created"
                >{{ $moment(folderDetail.created).fromNow() }}</span
                >
                </b-col>
              </b-row>
              <b-row>
                <b-col>
                  <b-button
                    id="rename-selected-folder"
                    class="m-1"
                    variant="secondary"
                    v-b-modal="'modal-rename-folder-mfp'"
                  >
                    {{ $t("Rename") }}
                  </b-button>
                  <b-button
                    id="move-selected-folder"
                    class="m-1"
                    variant="secondary"
                    v-b-modal="'modal-move-folder-mfp'"
                  >
                    {{ $t("Move") }}
                  </b-button>
                  <b-button
                    id="delete-selected-folder"
                    class="m-1"
                    variant="danger"
                    v-b-modal="'modal-delete-folder-mfp'"
                  >
                    {{ $t("Delete") }}
                  </b-button>
                </b-col>
              </b-row>
            </b-col>
          </b-row>
          <b-row v-else class="sticky-top">
            <b-col
            ><h1 class="text-muted">
              {{ $t("No folder selected") }}
            </h1></b-col
            >
          </b-row>
        </b-col>
      </b-row>

      <FTLRenameFolder
        v-if="folderDetail"
        modal-id="modal-rename-folder-mfp"
        :folder="folderDetail"
        @event-folder-renamed="folderUpdated"
      />

      <FTLNewFolder
        modal-id="modal-new-folder-mfp"
        :parent="getCurrentFolder"
        @event-folder-created="folderCreated"
      />

      <FTLDeleteFolder
        v-if="folderDetail"
        modal-id="modal-delete-folder-mfp"
        :folder="folderDetail"
        @event-folder-deleted="folderDeleted"
      />

      <FTLMoveFolder
        v-if="folderDetail"
        modal-id="modal-move-folder-mfp"
        :folder="folderDetail"
        @event-folder-moved="folderMoved"
      />
    </b-container>
  </b-modal>
</template>

<i18n>
  fr:
    Add: Ajouter
    Loading: Chargement
    No folder selected: Aucun dossier sélectionné
    Unable to get folder details: Les détails du dossier n'ont pu être récupérés
    Unable to refresh folders list: La liste des dossiers n'a pu être rafraichie
    Creation date: Date de création
    Could not open folder: Erreur lors de l'ouverture du dossier
    Folders management: Gestion des dossiers
</i18n>

<script>
import FTLSelectableFolder from "@/components/FTLSelectableFolder";
import FTLNewFolder from "@/components/FTLNewFolder";
import FTLRenameFolder from "@/components/FTLRenameFolder";
import FTLDeleteFolder from "@/components/FTLDeleteFolder";
import axios from "axios";
import FTLMoveFolder from "@/components/FTLMoveFolder";
import { mapGetters, mapState } from "vuex";

export default {
  name: "Folders",
  components: {
    FTLMoveFolder,
    FTLDeleteFolder,
    FTLRenameFolder,
    FTLSelectableFolder,
    FTLNewFolder,
  },
  props: {
    parentFolder: {
      default: null,
    },
    childrenFolders: {
      default: [],
    }
  },

  data() {
    return {
      // Folder panel
      folderDetail: null,
      folderDetailLoading: false,
    };
  },

  computed: {
    ...mapState(["previousLevels"]),
    ...mapGetters(["getCurrentFolder"])
  },

  methods: {
    getFolderDetails: function (folder) {
      if (!this.folderDetail || this.folderDetail.id !== folder.id) {
        this.folderDetailLoading = true;
        // Avoid duplicate request to folder detail api because when doubleclicking, it also triggers single click event
        axios
          .get("/app/api/v1/folders/" + folder.id)
          .then((response) => {
            this.folderDetail = response.data;
          })
          .catch((error) =>
            this.mixinAlert(this.$t("Unable to get folder details"), true)
          )
          .finally(() => {
            this.folderDetailLoading = false;
            // scroll to the bottom of the panel for mobile to see action buttons
            if (window.matchMedia("(max-width: 767px)").matches) {
              this.$nextTick(() => {
                const elem = document.querySelector("#right-panel");
                elem.scrollIntoView({
                  behavior: 'smooth',
                  block: "end",
                  inline: "nearest"
                })
              }
              );
            }
          })
      }
    },

    unselectFolder: function () {
      this.folderDetail = null;
    },

    folderCreated: function (folder) {
      folder.highlightAnimation = true;
      this.childrenFolders.unshift(folder);

      // update folders in Home
      this.$emit('update:childrenFolders', this.childrenFolders);
    },

    folderMoved: function (event) {
      const folderIndex = this._getFolderIndexFromId(event.folder.id);
      this.childrenFolders.splice(folderIndex, 1);

      this.unselectFolder();

      // update folders in Home
      this.$emit('update:childrenFolders', this.childrenFolders);
    },

    folderDeleted: function (event) {
      const folderId = event.folder.id;
      const folderIndex = this._getFolderIndexFromId(folderId);
      this.childrenFolders.splice(folderIndex, 1);

      this.unselectFolder();

      // if deleted folder match the one set for selectMoveTargetFolder, reset this state
      if (this.$store.getters.FTLTreeItemSelected(folderId)) {
        this.$store.commit("selectMoveTargetFolder", null);
      }

      // update folders in Home
      this.$emit('update:childrenFolders', this.childrenFolders);
    },

    folderUpdated: function (event) {
      const folder = event.folder;
      const folderIndex = this._getFolderIndexFromId(folder.id);
      this.$set(this.childrenFolders, folderIndex, folder); // to be reactive, see https://vuejs.org/v2/guide/list.html#Caveats
      if (this.folderDetail && this.folderDetail.id === folder.id) {
        this.folderDetail = folder;
      }

      // update folders in Home
      this.$emit('update:childrenFolders', this.childrenFolders);
    },

    _getFolderIndexFromId(folderId) {
      return this.childrenFolders.findIndex((x) => x.id === folderId);
    },
  },
};
</script>

<style lang="scss">
@import "~bootstrap/scss/_functions.scss";
@import "~bootstrap/scss/_variables.scss";
@import "~bootstrap/scss/_mixins.scss";
$manage-folders-padding: 2em;

#modal-manage-folders {
  .container {
    max-width: none;
  }

  .modal-dialog {
    width: 100vw;
    max-width: none;
    margin: 0;
  }

  .fa-folder {
    width: 1.125em;
  }

  #parent-folder,
  #title-separator,
  #title {
    display: block;
    padding: 1rem;
    margin: -1rem -1rem -1rem auto;
  }

  #parent-folder {
    max-width: 25%;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding-left: 0;

    &:hover {
      .fa-folder {
        display: none !important;
      }

      .fa-folder-open {
        display: inline-block !important;
      }
    }
  }

  #title-separator {
    padding: 1rem 0.5rem;
  }

  #title {
    max-width: 65%;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .close {
    line-height: 1.25;
  }

  .modal-content {
    height: calc(100vh - (#{$manage-folders-padding} * 2));
  }

  #create-folder {
    cursor: pointer;
    border: 3px solid transparent;
  }

  #right-panel {
    border-top: 2px solid map_get($theme-colors, "light-gray");
    padding-top: 1em;
    min-height: 250px;
  }
}

@include media-breakpoint-up(md) {
  #modal-manage-folders {
    .modal-dialog {
      padding: $manage-folders-padding;
    }

    #right-panel {
      border-top: 0;
      border-left: 2px solid map_get($theme-colors, "light-gray");
      margin-top: 0;
      padding-top: 0;
    }
  }
}
</style>
