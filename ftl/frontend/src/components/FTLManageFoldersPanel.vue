<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <b-modal
    id="folders-mngt"
    hide-footer
    centered
    scrollable
    :title="$t('Folders management')"
    body-class="px-0"
    @hidden="$bvModal.hide('folders-mngt')"
  >
    <main class="flex-grow">
      <b-container fluid class="text-center">
        <b-row>
          <!-- Left panel -->
          <b-col id="left-panel" md="8">
            <b-row>
              <b-col>
                <b-breadcrumb
                  class="breadcrumb-ftl"
                  :items="breadcrumb"
                  @click="unselectFolder"
                />
              </b-col>
            </b-row>
            <b-row v-if="foldersLoading">
              <b-col>
                <b-spinner
                  style="width: 3rem; height: 3rem;"
                  class="m-5 loader"
                  label="Loading..."
                ></b-spinner>
              </b-col>
            </b-row>
            <b-row align-h="center" v-else>
              <FTLSelectableFolder
                v-for="_folder in folders"
                :key="_folder.id"
                :folder="_folder"
                @event-navigate-folder="navigateToFolder"
                @event-select-folder="getFolderDetail"
                @event-unselect-folder="unselectFolder"
              />
              <b-col
                id="create-folder"
                sm="2"
                class="m-1"
                v-b-modal="'modal-new-folder'"
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
                  ><b>{{ $t("Create new folder") }}</b></b-col
                  >
                </b-row>
              </b-col>
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
                      v-b-modal="'modal-rename-folder'"
                    >
                      {{ $t("Rename") }}
                    </b-button>
                    <b-button
                      id="move-selected-folder"
                      class="m-1"
                      variant="secondary"
                      v-b-modal="'modal-move-folder'"
                    >
                      {{ $t("Move") }}
                    </b-button>
                    <b-button
                      id="delete-selected-folder"
                      class="m-1"
                      variant="danger"
                      v-b-modal="'modal-delete-folder'"
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
          :folder="folderDetail"
          @event-folder-renamed="folderUpdated"
        />

        <FTLNewFolder
          :parent="getCurrentFolder"
          @event-folder-created="folderCreated"
        />

        <FTLDeleteFolder
          v-if="folderDetail"
          :folder="folderDetail"
          @event-folder-deleted="folderDeleted"
        />

        <FTLMoveFolder
          v-if="folderDetail"
          :folder="folderDetail"
          @event-folder-moved="folderMoved"
        />
      </b-container>
    </main>
  </b-modal>
</template>

<i18n>
  fr:
    Create new folder: Créer un nouveau dossier
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
  props: ["folder"],

  data() {
    return {
      // Folders list
      foldersLoading: false,
      folders: [],

      // Folder panel
      folderDetail: null,
      folderDetailLoading: false,
    };
  },

  watch: {
    folder: function (newVal, oldVal) {
      if (newVal === undefined) {
        this.$store.commit('resetPreviousLevels');
        this.updateFolders();
      } else {
        if (newVal !== oldVal) {
          // Restore breadcrumb
          this.updateFoldersFromUrl(newVal);
        }
      }
    },
  },

    mounted() {
      if (this.folder) {
        this.updateFoldersFromUrl(this.folder);
      } else {
        this.updateFolders();
      }
    },

  computed: {
    breadcrumb: function () {
      let paths = [];

      paths.push({
        text: this.$t("Root"),
        to: { name: "folders" },
      });

      return paths.concat(
        this.previousLevels.map((e) => {
          return {
            text: e.name,
            to: {
              name: "folders",
              params: { folder: e.id },
            },
          };
        })
      );
    },
    ...mapState(["previousLevels"]),
    ...mapGetters(["getCurrentFolder"])
  },

  methods: {
    refreshFolder: function () {
      if (this.folder) {
        this.updateFoldersFromUrl(this.folder);
      } else {
        this.$store.commit('resetPreviousLevels');
        this.updateFolders();
      }
    },

    getFolderDetail: function (folder) {
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

    navigateToFolder: function (folder) {
      this.unselectFolder();
      if (folder) this.$store.commit('appendNewLevel', folder);
      this.$router.push({
        name: "folders",
        params: { folder: folder.id },
      });
    },

    updateFolders: function (folder = null) {
      const vi = this;
      let qs = "";

      vi.foldersLoading = true;

      if (folder) {
        if ("has_descendant" in folder && folder.has_descendant === false) {
          // Avoid doing an API request when we know there are no descendant
          vi.folders = [];
          vi.foldersLoading = false;
          return;
        }

        qs = "?level=" + folder.id;
      }

      axios
        .get("/app/api/v1/folders" + qs)
        .then((response) => {
          vi.folders = response.data;
        })
        .catch((error) =>
          vi.mixinAlert(vi.$t("Unable to refresh folders list"), true)
        )
        .finally(() => (vi.foldersLoading = false));
    },

    updateFoldersFromUrl: function (folderId) {
      this.foldersLoading = true;

      if (this.folderDetail && this.folderDetail.id === folderId) {
        // Avoid duplicate request to folder detail api if we have already the detail because we clicked on the folder
        this.$store.commit('setPreviousLevels', this.folderDetail.paths);
        this.updateFolders(this.folderDetail);
      } else {
        axios
          .get("/app/api/v1/folders/" + folderId)
          .then((response) => {
            this.$store.commit('setPreviousLevels', response.data.paths);
            this.updateFolders(response.data);
          })
          .catch(() => {
            this.mixinAlert(this.$t("Could not open folder"), true);
            this.foldersLoading = false;
          });
      }
    },

    folderCreated: function (folder) {
      folder.highlightAnimation = true;
      this.folders.push(folder);
    },

    folderMoved: function (event) {
      const folderIndex = this._getFolderIndexFromId(event.folder.id);
      this.folders.splice(folderIndex, 1);

      this.unselectFolder();
    },

    folderDeleted: function (event) {
      const folderId = event.folder.id;
      const folderIndex = this._getFolderIndexFromId(folderId);
      this.folders.splice(folderIndex, 1);

      this.unselectFolder();

      // if deleted folder match the one set for selectMoveTargetFolder, reset this state
      if (this.$store.getters.FTLTreeItemSelected(folderId)) {
        this.$store.commit("selectMoveTargetFolder", null);
      }
    },

    folderUpdated: function (event) {
      const folder = event.folder;
      const folderIndex = this._getFolderIndexFromId(folder.id);
      this.$set(this.folders, folderIndex, folder); // to be reactive, see https://vuejs.org/v2/guide/list.html#Caveats
      if (this.folderDetail && this.folderDetail.id === folder.id) {
        this.folderDetail = folder;
      }
    },

    _getFolderIndexFromId(folderId) {
      return this.folders.findIndex((x) => x.id === folderId);
    },
  },
};
</script>

<style lang="scss">
@import "~bootstrap/scss/_functions.scss";
@import "~bootstrap/scss/_variables.scss";
@import "~bootstrap/scss/_mixins.scss";
$manage-folders-padding: 2em;

#folders-mngt {
  .container {
    max-width: none;
  }

  .modal-dialog {
    width: 100vw;
    max-width: none;
    margin: 0;
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
  #folders-mngt {
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
