<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <main class="flex-grow">
    <b-col>
      <b-row class="my-3">
        <b-col>
          <FTLUpload
            :currentFolder="getCurrentFolder"
            @event-new-upload="documentsCreatedExtended"
          />
        </b-col>
      </b-row>

      <b-row class="my-3" id="breadcrumb" no-gutter>
        <b-col>
          <b-breadcrumb class="breadcrumb-ftl m-0">
            <FTLBreadcrumbFolder
              v-for="(item, index) in breadcrumb"
              :key="item.id"
              :id="item.id"
              :text="item.text"
              :to="item.to"
              :active="index === breadcrumb.length - 1"
              :folder="{ id: item.id, name: item.text }"
              @event-document-moved="documentDeleted"
            />
          </b-breadcrumb>
        </b-col>
      </b-row>

      <b-row
        v-show="!selectedDocumentsHome.length"
        class="mt-3"
        id="folders-list"
      >
        <b-col>
          <b-button
            id="refresh-documents"
            :disabled="docsLoading"
            variant="primary"
            @click="refreshAll"
          >
            <font-awesome-icon
              icon="sync"
              :spin="docsLoading"
              :class="{ 'stop-spin': !docsLoading }"
              :title="$t('Refresh documents list')"
            />
          </b-button>
          <b-button
            id="create-folder"
            variant="primary"
            v-b-modal="'modal-new-folder'"
          >
            <font-awesome-icon
              icon="folder-plus"
              :title="$t('Create new folder')"
            />
          </b-button>
          <b-button
            variant="primary"
            :disabled="!previousLevels.length"
            @click="changeToPreviousFolder"
          >
            <font-awesome-icon icon="level-up-alt" />
          </b-button>
          <FTLFolder
            v-for="folder in folders"
            :key="folder.id"
            :folder="folder"
            @event-change-folder="navigateToFolder"
            @event-document-moved="documentDeleted"
          />

          <b-dropdown
            id="documents-sort"
            right
            variant="link"
            class="m-1 text-decoration-none"
          >
            <template slot="button-content">
              <font-awesome-icon icon="sort" />
              {{ $t("Sort") }}
              <span v-if="sort === 'az'">({{ $t("A-Z") }})</span>
              <span v-else-if="sort === 'za'">({{ $t("Z-A") }})</span>
              <span v-else-if="sort === 'recent'"
                >({{ $t("Recent first") }})</span
              >
              <span v-else-if="sort === 'older'"
                >({{ $t("Older first") }})</span
              >
            </template>
            <b-dropdown-item-button
              id="az-sort"
              href="#"
              @click.prevent="sort = 'az'"
              >{{ $t("A-Z") }}&nbsp;
              <span v-if="sort === 'az'"
                >&checkmark;</span
              ></b-dropdown-item-button
            >
            <b-dropdown-item-button
              id="za-sort"
              href="#"
              @click.prevent="sort = 'za'"
              >{{ $t("Z-A") }}&nbsp;
              <span v-if="sort === 'za'"
                >&checkmark;</span
              ></b-dropdown-item-button
            >
            <b-dropdown-divider />
            <b-dropdown-item-button
              id="recent-sort"
              href="#"
              @click.prevent="sort = 'recent'"
              >{{ $t("Recent first") }}&nbsp;
              <span v-if="sort === 'recent'"
                >&checkmark;</span
              ></b-dropdown-item-button
            >
            <b-dropdown-item-button
              id="older-sort"
              href="#"
              @click.prevent="sort = 'older'"
              >{{ $t("Older first") }}&nbsp;
              <span v-if="sort === 'older'"
                >&checkmark;</span
              ></b-dropdown-item-button
            >
          </b-dropdown>
        </b-col>
      </b-row>

      <b-row
        v-show="selectedDocumentsHome.length"
        class="mb-3"
        id="action-selected-documents"
      >
        <b-col>
          <b-button
            id="select-all-documents"
            variant="outline-primary"
            :title="$t('Select all documents displayed')"
            @click="$store.commit('selectDocuments', docs)"
          >
            {{ $t("Select all") }}
          </b-button>
        </b-col>
        <b-col cols="8" class="text-right">
          <span class="text-muted d-none d-sm-inline">{{
            $tc("| 1 document: | {n} documents:", selectedDocumentsHome.length)
          }}</span>
          <b-button
            id="unselect-all-documents"
            @click="$store.commit('unselectAllDocuments')"
            :title="$t('Deselect all documents')"
          >
            <font-awesome-icon icon="window-close" class="d-sm-none" />
            <span class="d-none d-sm-inline">{{ $t("Cancel") }}</span>
          </b-button>
          <b-button
            id="move-documents"
            variant="primary"
            v-b-modal="'modal-move-documents'"
            :title="$t('Move to folder')"
          >
            <font-awesome-icon icon="folder-open" class="d-sm-none" />
            <span class="d-none d-sm-inline">{{ $t("Move") }}</span>
          </b-button>
          <b-button
            id="delete-documents"
            variant="danger"
            v-b-modal="'modal-delete-documents'"
            :title="$t('Delete documents')"
          >
            <font-awesome-icon icon="trash" class="d-sm-none" />
            <span class="d-none d-sm-inline">{{ $t("Delete") }}</span>
          </b-button>
        </b-col>
      </b-row>

      <b-row class="mt-2 mb-3" id="documents-list">
        <b-col v-if="docsLoading">
          <b-spinner
            class="mx-auto loader"
            id="documents-list-loader"
            label="Loading..."
          ></b-spinner>
        </b-col>
        <b-col v-else-if="docs.length">
          <b-row tag="section">
            <FTLDocument
              v-for="doc in docs"
              :key="doc.pid"
              :doc="doc"
              @event-open-doc="navigateToDocument"
              @event-rename-doc="renameDoc"
            />
          </b-row>
        </b-col>
        <b-col v-else class="text-center">{{ $t("No document yet") }}</b-col>
      </b-row>

      <b-row v-if="moreDocs" align-h="center" class="my-3">
        <b-col>
          <b-button
            id="more-documents"
            block
            variant="secondary"
            @click.prevent="loadMoreDocuments"
          >
            <b-spinner
              class="loader"
              :class="{ 'd-none': !moreDocsLoading }"
              small
            ></b-spinner>
            <span :class="{ 'd-none': moreDocsLoading }">
              {{
                $tc(
                  "| Show more documents (1 remaining) | Show more documents ({n} remaining)",
                  count - docs.length
                )
              }}
            </span>
          </b-button>
        </b-col>
      </b-row>

      <!-- Pdf viewer popup -->
      <FTLDocumentPanel
        v-if="docPid"
        :pid="docPid"
        @event-document-panel-closed="documentClosed"
        @event-document-moved="documentDeleted"
        @event-document-deleted="documentDeleted"
      />

      <FTLNewFolder
        :parent="getCurrentFolder"
        @event-folder-created="folderCreated"
      />

      <!-- For batch action move document -->
      <FTLMoveDocuments
        v-if="selectedDocumentsHome.length > 0"
        id="modal-move-documents"
        :docs="selectedDocumentsHome"
        @event-document-moved="documentDeleted"
      />

      <FTLDeleteDocuments
        v-if="selectedDocumentsHome.length > 0"
        :docs="selectedDocumentsHome"
        @event-document-deleted="documentDeleted"
      />

      <FTLRenameDocument
        :doc="currentRenameDoc"
        id="modal-rename-document-home"
        @event-document-renamed="documentUpdated"
      />
    </b-col>
  </main>
</template>

<i18n>
  fr:
    Refresh documents list: Rafraichir la liste des documents
    Create new folder: Créer un nouveau dossier
    Sort: Trier
    Recent first: Récents en premier
    Older first: Anciens en premier
    A-Z: A-Z
    Z-A: Z-A
    Select all: Tout sélectionner
    "| 1 document: | {n} documents:": "| 1 document : | {n} documents :"
    No document yet: Aucun document
    "| Show more documents (1 remaining) | Show more documents ({n} remaining)": "| Afficher plus de documents (1 restant) | Afficher plus de documents ({n} restants)"
    Could not open this folder.: Impossible d'ouvrir ce dossier.
    Select all documents displayed: Sélectionner tous les documents affichés
    Deselect all documents: Désélectionner tous les documents
    Move to folder: Déplacer vers le dossier
    Delete documents: Supprimer les documents
    Unable to refresh folders list: Erreur lors du chargement de la liste des dossiers
</i18n>

<script>
// @ is an alias to /src
import { mapState } from "vuex";
import HomeBase from "@/views/HomeBase";
import FTLFolder from "@/components/FTLFolder.vue";
import FTLNewFolder from "@/components/FTLNewFolder";
import FTLDocumentPanel from "@/components/FTLDocumentPanel";
import FTLDeleteDocuments from "@/components/FTLDeleteDocuments";
import FTLMoveDocuments from "@/components/FTLMoveDocuments";
import FTLDocument from "@/components/FTLDocument";
import FTLUpload from "@/components/FTLUpload";
import FTLRenameDocument from "@/components/FTLRenameDocument";
import FTLBreadcrumbFolder from "@/components/FTLBreadcrumbFolder";
import axios from "axios";
import Driver from "driver.js";
import "driver.js/dist/driver.min.css";

export default {
  name: "home",
  extends: HomeBase,

  components: {
    FTLNewFolder,
    FTLFolder,
    FTLDocumentPanel,
    FTLDeleteDocuments,
    FTLMoveDocuments,
    FTLDocument,
    FTLUpload,
    FTLRenameDocument,
    FTLBreadcrumbFolder,
  },

  props: ["folder"],

  data() {
    return {
      sort: "recent",

      // Folders list and breadcrumb
      folders: [],
      previousLevels: [],
    };
  },

  mounted() {
    this.sort = String(this.sortHome); // copy value for sortHome mutations not to call sort watcher

    if (this.folder) {
      // Open folder directly from loading an URL with folder (don't reset URL if opening a document)
      this.updateFoldersPath(this.folder);
    } else {
      // Or just show the current folders
      this.refreshFolders();
      this.updateDocuments();
    }

    // Clear the selected documents
    this.$store.commit("unselectAllDocuments");

    // Tour
    if (!localStorage.tour_done) {
      this.$nextTick(function () {
        const driver = new Driver({
          // animate: false,
          stageBackground: "transparent",
          opacity: 0,
          allowClose: false,
          overlayClickNext: false,
          showButtons: true,
          doneBtnText: this.$t("Done"),
          closeBtnText: this.$t("Close"),
          nextBtnText: this.$t("Next"),
          prevBtnText: this.$t("Previous"),
        });

        driver.defineSteps([
          {
            element: "#upload-section",
            popover: {
              title: "Envoyer vos documents",
              description:
                "Sélectionner vos documents à envoyer ou glisser-déposer vos documents dans la zone.",
              position: "bottom-center",
            },
          },
          {
            element: "#search-zone",
            popover: {
              title: "Rechercher vos documents",
              description:
                "Indiquer un ou plusieurs mots clés représentatives de vos documents.",
              position: "bottom-center",
            },
          },
          {
            element: "#breadcrumb",
            popover: {
              title: "Arborescence parcourue",
              description:
                "Votre fils d'ariane indiquant le chemin parcouru jusqu'au dossier actuel.",
              position: "bottom",
              offset: 20,
            },
          },
          {
            element: "#folders-list",
            popover: {
              title: "Dossiers",
              description:
                "Vos dossiers du répertoire courant. Vous pouvez aussi créer un nouveau dossier ou revenir au dossier précédent.",
              position: "bottom",
              offset: 20,
            },
          },
          {
            element: "#documents-list",
            popover: {
              title: "Documents",
              description:
                "Vos documents du dossier courant ou bien les résultats de votre recherche.",
              position: "top-center",
            },
          },
        ]);

        driver.start();
      });
      localStorage.tour_done = true;
    }
  },

  watch: {
    folder: function (newVal, oldVal) {
      if (this.$route.name === "home") {
        // Coming back to home so clear everything and reload from root folder
        this.changeFolder();
      } else if (this.$route.name === "home-folder") {
        // This is navigation between folders
        if (newVal !== oldVal) {
          this.updateFoldersPath(newVal);
        }
      }

      // Clear the selected documents when moving between folders
      this.$store.commit("unselectAllDocuments");
    },
    sort: function (newVal, oldVal) {
      if (newVal !== oldVal) {
        this.updateDocuments();
        this.$store.commit("changeSortHome", newVal);
      }
    },
  },

  computed: {
    getCurrentFolder: function () {
      if (this.previousLevels.length) {
        return this.previousLevels[this.previousLevels.length - 1];
      } else {
        return null;
      }
    },

    breadcrumb: function () {
      const vi = this;
      let paths = [];

      paths.push({
        id: null,
        text: this.$t("Root"),
        to: { name: "home" },
      });

      paths = paths.concat(
        this.previousLevels.map((e) => {
          return {
            id: e.id,
            text: e.name,
            to: {
              path: "/home/" + vi.computeFolderUrlPath(e.id),
            },
          };
        })
      );

      // Add total documents count after current folder name
      paths[paths.length - 1].text =
        this.count > 0
          ? `${paths[paths.length - 1].text} (${this.count})`
          : `${paths[paths.length - 1].text}`;

      return paths;
    },
    ...mapState(["selectedDocumentsHome", "sortHome"]), // generate vuex computed getter
  },

  methods: {
    computeFolderUrlPath: function (id = null) {
      if (this.previousLevels.length > 0) {
        let s = this.previousLevels.map((e) => e.name);

        if (id) {
          s.push(id);
        } else {
          s.push(this.previousLevels[this.previousLevels.length - 1].id);
        }

        return s.join("/");
      } else {
        return "";
      }
    },

    refreshFolders: function () {
      this.updateFolders(this.getCurrentFolder);
    },

    refreshAll: function () {
      this.refreshFolders();
      this.updateDocuments();
    },

    changeFolder: function (folder = null) {
      if (folder === null) {
        this.previousLevels = [];
      }
      this.updateFolders(folder);
      this.updateDocuments();
    },

    navigateToFolder: function (folder) {
      if (folder) this.previousLevels.push(folder);
      this.$router.push({
        path: "/home/" + this.computeFolderUrlPath(folder.id),
      });
    },

    changeToPreviousFolder: function () {
      this.previousLevels.pop(); // Remove current level
      let level = this.getCurrentFolder;

      if (level === null) {
        this.$router.push({ name: "home" });
      } else {
        this.$router.push({
          path: "/home/" + this.computeFolderUrlPath(level.parent),
        });
      }
    },

    updateFoldersPath: function (folderId) {
      axios
        .get("/app/api/v1/folders/" + folderId)
        .then((response) => {
          this.previousLevels = response.data.paths;
          this.changeFolder(response.data);
          // Allow refresh of the current URL in address bar to take into account folders paths changes
          if (this.docPid) {
            this.$router.push(
              {
                path: "/home/" + this.computeFolderUrlPath(folderId),
                query: {
                  doc: this.docPid,
                },
              },
              () => {}
            );
          } else {
            this.$router.push(
              {
                path: "/home/" + this.computeFolderUrlPath(folderId),
              },
              () => {}
            );
          }
        })
        .catch((error) => {
          this.mixinAlert(this.$t("Could not open this folder."), true);
        });
    },

    documentsCreatedExtended: function (event) {
      const doc = event.doc;
      // Only add document to interface if we are in the same folder, this should allow the user to navigate while uploading
      if (this.folder) {
        if (parseInt(this.folder, 10) === doc.ftl_folder) {
          this.documentsCreated(event);
        }
      } else {
        if (!doc.ftl_folder) {
          // In root folder and document has no folder
          this.documentsCreated(event);
        }
      }
    },

    updateDocuments: function () {
      let queryString = {};

      if (this.previousLevels.length > 0) {
        queryString["level"] = this.getCurrentFolder.id;
      }

      return this._updateDocuments(queryString);
    },

    updateFolders: function (level = null) {
      const vi = this;
      let qs = "";

      if (level) {
        if ("has_descendant" in level && level.has_descendant === false) {
          // Avoid doing an API request when we know there are no descendant
          vi.folders = [];
          return;
        }

        qs = "?level=" + level.id;
      }

      axios
        .get("/app/api/v1/folders" + qs)
        .then((response) => {
          vi.folders = response.data;
        })
        .catch((error) =>
          vi.mixinAlert(this.$t("Unable to refresh folders list"), true)
        );
    },

    folderCreated: function (folder) {
      this.refreshFolders();
    },
  },
};
</script>

<style scoped lang="scss">
@import "~bootstrap/scss/_functions.scss";
@import "~bootstrap/scss/_variables.scss";
@import "~bootstrap/scss/_mixins.scss";

#documents-list-loader {
  width: 3em;
  height: 3em;
  display: block;
}

#folders-list button {
  margin-left: 0 !important;
  margin-right: 0.5rem !important;
  margin-bottom: 0.5rem !important;
}

#action-selected-documents button,
#action-selected-documents span {
  margin-left: 0 !important;
  margin-right: 0.5rem !important;

  &:last-child {
    margin-right: 0 !important;
  }
}

#action-selected-documents {
  position: sticky;
  top: 72px;
  animation: slide-down 0.1s linear;
  z-index: calc(
    #{$zindex-sticky} - 1
  ); // to be under header dropdown menu (mobile)
  background: $light;
}

@include media-breakpoint-up(sm) {
  #action-selected-documents {
    top: 56px;
  }
}

.stop-spin {
  animation: unspin 0.5s 1 ease-out;
}
</style>

<style lang="scss">
#documents-sort {
  float: right;
  margin-top: 0 !important;
  margin-right: 0 !important;

  .btn {
    padding-right: 0 !important;
    border-right: none !important;
  }
}
</style>
