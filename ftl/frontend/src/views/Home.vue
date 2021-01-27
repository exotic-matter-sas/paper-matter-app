<!--
  - Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
  - Licensed under the Business Source License. See LICENSE at project root for more information.
  -->

<template>
  <main class="flex-grow">
    <b-col>
      <b-row>
        <b-col>
          <FTLUpload
            :files-to-upload.sync="droppedFiles"
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
            v-b-modal="'modal-new-folder-h'"
          >
            <font-awesome-icon
              icon="folder-plus"
              :title="$t('Create new folder')"
              size="lg"
            />
          </b-button>
          <b-button
            id="manage-folders"
            variant="primary"
            :title="$t('Rename or move folder')"
            v-b-modal="'modal-manage-folders'"
          >
            <svg
              class="svg-inline--fa fa-folder fa-w-16 fa-lg"
              width="512"
              height="512"
              aria-hidden="true"
              data-icon="folder"
              data-prefix="fas"
              focusable="false"
              role="img"
              version="1.1"
              viewBox="0 0 512 512"
              xmlns="http://www.w3.org/2000/svg"
            >
              <g transform="translate(0 -.012176)">
                <path
                  transform="translate(0 .012176)"
                  d="m48 64c-26.51 0-48 21.49-48 48v288c0 26.51 21.49 48 48 48h416c26.51 0 48-21.49 48-48v-224c0-26.51-21.49-48-48-48h-192l-64-64h-160zm299.01 100.57c5.3568 0 10.712 2.0347 14.779 6.1016l33.146 33.146c8.1336 8.2211 8.1336 21.427 0 29.648l-36.557 36.557-62.795-62.707 36.645-36.645c4.0668-4.0668 9.4244-6.1016 14.781-6.1016zm-71.191 62.512 62.707 62.707-120.61 120.61-53.262 5.9473c-8.8333 1.0495-16.355-6.4718-15.393-15.393l5.9473-53.35 120.61-120.52z"
                  fill="currentColor"
                />
              </g>
            </svg>
          </b-button>
          <b-button
            variant="primary"
            :disabled="!previousLevels.length"
            :title="$t('Back to parent folder')"
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
            v-if="docs.length === selectedDocumentsHome.length"
            id="unselect-all-documents"
            variant="outline-primary"
            @click="$store.commit('unselectAllDocuments')"
            :title="$t('Deselect all documents')"
          >
            {{ $t("Deselect all") }}
          </b-button>
          <b-button
            v-else
            id="select-all-documents"
            variant="outline-primary"
            :title="$t('Select all documents displayed')"
            @click="$store.commit('selectDocuments', docs)"
          >
            {{ $t("Select all") }}
          </b-button>
        </b-col>
        <b-col cols="7" class="text-right">
          <span class="text-muted d-none d-sm-inline d-md-none">{{
            $tc("| 1 doc: | {n} docs:", selectedDocumentsHome.length)
          }}</span>
          <span class="text-muted d-none d-md-inline">{{
            $tc("| 1 document: | {n} documents:", selectedDocumentsHome.length)
          }}</span>
          <b-button
            id="cancel-selection"
            class="d-none d-md-inline-block"
            @click="$store.commit('unselectAllDocuments')"
            :title="$t('Deselect all documents')"
          >
            {{ $t("Cancel") }}
          </b-button>
          <b-button
            id="move-documents"
            variant="primary"
            v-b-modal="'modal-move-documents-h'"
            :title="$t('Move to folder')"
          >
            <font-awesome-icon icon="folder-open" class="d-sm-none" />
            <span class="d-none d-sm-inline">{{ $t("Move") }}</span>
          </b-button>
          <b-button
            id="delete-documents"
            variant="danger"
            v-b-modal="'modal-delete-documents-h'"
            :title="$t('Delete documents')"
          >
            <font-awesome-icon icon="trash" class="d-sm-none" />
            <span class="d-none d-sm-inline">{{ $t("Delete") }}</span>
          </b-button>
        </b-col>
      </b-row>

      <b-row
        class="mt-2 mb-3"
        id="documents-list"
        :class="{ 'documents-list-dragged-hover': draggingFilesToDocsList }"
        @dragenter="showDropZone"
        @dragover="allowDrop"
        @drop="getDroppedFiles"
        @dragleave.self="hideDropZone"
        @mouseover="hideDropZone"
      >
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
        <div
          v-show="draggingFilesToDocsList"
          id="document-drop-overlay"
          class="position-fixed w-100 text-center font-weight-bold"
        >
          <div id="document-drop-label" class="w-100 my-5">
            <img
              class="mb-3"
              src="@/assets/add_files.svg"
              alt="Add files illustration"
            />
            <br />
            <p class="mb-3">{{ $t("Drop documents to upload.") }}</p>
          </div>
        </div>
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
        :docs="docs"
        @event-document-panel-closed="documentClosed"
        @event-document-moved="documentDeleted"
        @event-document-deleted="documentDeleted"
        @event-change-document="navigateToDocument"
      />

      <FTLNewFolder
        modal-id="modal-new-folder-h"
        :parent="getCurrentFolder"
        @event-folder-created="folderCreated"
      />

      <FTLManageFoldersPanel
        :parent-folder="getCurrentFolder"
        :children-folders.sync="folders"
        @event-folder-created="folderCreated"
        @event-folder-renamed="folderUpdated"
        @event-folder-moved="folderDeleted"
        @event-folder-deleted="folderDeleted"
      />

      <!-- For batch action -->
      <FTLMoveDocuments
        v-if="selectedDocumentsHome.length > 0"
        modal-id="modal-move-documents-h"
        :docs="selectedDocumentsHome"
        @event-document-moved="documentDeleted"
      />

      <!-- For batch action -->
      <FTLDeleteDocuments
        v-if="selectedDocumentsHome.length > 0"
        modal-id="modal-delete-documents-h"
        :docs="selectedDocumentsHome"
        @event-document-deleted="documentDeleted"
      />

      <FTLRenameDocument
        modal-id="modal-rename-document-h"
        :doc="currentRenameDoc"
        @event-document-renamed="documentUpdated"
      />
    </b-col>
  </main>
</template>

<i18n>
  fr:
    Root: Racine
    Refresh documents list: Rafraichir la liste des documents
    Create new folder: Créer un nouveau dossier
    Sort: Trier
    Recent first: Récents en premier
    Older first: Anciens en premier
    A-Z: A-Z
    Z-A: Z-A
    Select all: Tout sélectionner
    Deselect all: Tout désélectionner
    "| 1 doc: | {n} docs:": "| 1 doc : | {n} docs :"
    "| 1 document: | {n} documents:": "| 1 document : | {n} documents :"
    No document yet: Aucun document
    "| Show more documents (1 remaining) | Show more documents ({n} remaining)": "| Afficher plus de documents (1 restant) | Afficher plus de documents ({n} restants)"
    Could not open this folder: Impossible d'ouvrir ce dossier
    Select all documents displayed: Sélectionner tous les documents affichés
    Deselect all documents: Désélectionner tous les documents
    Move to folder: Déplacer vers le dossier
    Delete documents: Supprimer les documents
    Unable to refresh folders list: Erreur lors du chargement de la liste des dossiers
    Done: Terminer
    Next: Suivant
    Previous: Précédent
    Close: Fermer
    Add documents (1/5): Ajouter vos documents 1/5
    Click on <b>Add documents</b>.: Cliquez sur <b>Ajouter des documents</b>.
    Add documents (2/5): Ajouter vos documents 2/5
    You can also drag n drop files straight into the documents list.: Vous pouvez aussi glisser-déposer vos fichers directement dans la liste des documents.
    Find documents (2/5): Retrouver vos documents (2/5)
    Type keywords contained in the document title, content or note and hit <b>Search</b> button.: Saisissez des mots-clés contenus dans le titre, contenu ou note du document et cliquez sur le bouton <b>Rechercher</b>.
    Current folder path (3/5): Chemin du dossier courant (3/5)
    The breadcrumb shows you the path of the current folder and allows you to quickly navigate to its parents.: Le fil d'ariane vous montre le chemin du dossier courant et vous permet de naviguer rapidement vers ses parents.
    Folders (4/5): Dossier (4/5)
    Your folders list, you can create a new folder or go back to the parent folder when you are inside a sub folder.: La liste de vos dossiers, vous pouvez créer un nouveau dossier ou revenir au dossier parent lorsque vous êtes dans un sous-dossier.
    Documents (5/5): Documents (5/5)
    "Your documents list, you can select multiple documents using the checkboxes (or <kbd>Ctrl</kbd> + <kbd>Left click</kbd>) to apply batch actions.<br/>To quickly add new documents drag n drop them straight into the list.": "La liste de vos documents, vous pouvez en sélectionner plusieurs avec les cases à cocher (ou <kbd>Ctrl</kbd> + <kbd>Clic gauche</kbd>) pour réaliser des actions groupées.<br/>Pour ajouter rapidement des fichiers, glissez-déposez les directement dans la liste."
    Rename or move folder: Renommer ou déplacer un dossier
    Back to parent folder: Revenir au dossier parent
    Drop documents to upload.: Déposez les documents pour les ajouter.
</i18n>

<script>
// @ is an alias to /src
import { mapGetters, mapState } from "vuex";
import HomeBase from "@/views/HomeBase";
import FTLFolder from "@/components/FTLFolder.vue";
import FTLNewFolder from "@/components/FTLNewFolder";
import FTLManageFoldersPanel from "@/components/FTLManageFoldersPanel";
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
    FTLManageFoldersPanel,
    FTLDocumentPanel,
    FTLDeleteDocuments,
    FTLMoveDocuments,
    FTLDocument,
    FTLUpload,
    FTLRenameDocument,
    FTLBreadcrumbFolder,
  },

  props: ["folderId"],

  data() {
    return {
      sort: "recent",
      folders: [],
    };
  },

  mounted() {
    this.sort = String(this.sortHome); // copy value for sortHome mutations not to call sort watcher

    if (this.folderId) {
      // Open folder directly from loading an URL with folder (don't reset URL if opening a document)
      this.updateFoldersPath(this.folderId);
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
          opacity: 0.7,
          allowClose: false,
          overlayClickNext: false,
          showButtons: true,
          doneBtnText: this.$t("Done"),
          closeBtnText: this.$t("Close"),
          nextBtnText: this.$t("Next"),
          prevBtnText: this.$t("Previous"),
          onReset: (elem) => {
            localStorage.tour_done = true;
          },
        });

        driver.defineSteps([
          {
            element: "#add-documents",
            popover: {
              title: this.$t("Add documents (1/5)"),
              description: this.$t("Click on <b>Add documents</b>."),
              position: "bottom-center",
            },
          },
          {
            element: "#search-zone",
            popover: {
              title: this.$t("Find documents (2/5)"),
              description: this.$t(
                "Type keywords contained in the document title, content or note and hit <b>Search</b> button."
              ),
              position: "bottom-center",
            },
          },
          {
            element: "#breadcrumb",
            popover: {
              title: this.$t("Current folder path (3/5)"),
              description: this.$t(
                "The breadcrumb shows you the path of the current folder and allows you to quickly navigate to its parents."
              ),
              position: "bottom",
              offset: 20,
            },
          },
          {
            element: "#folders-list",
            popover: {
              title: this.$t("Folders (4/5)"),
              description: this.$t(
                "Your folders list, you can create a new folder or go back to the parent folder when you are inside a sub folder."
              ),
              position: "bottom",
              offset: 20,
            },
          },
          {
            element: "#documents-list",
            popover: {
              title: this.$t("Documents (5/5)"),
              description: this.$t(
                "Your documents list, you can select multiple documents using the checkboxes (or <kbd>Ctrl</kbd> + <kbd>Left click</kbd>) to apply batch actions.<br/>To quickly add new documents drag n drop them straight into the list."
              ),
              position: "mid-center",
            },
          },
        ]);

        driver.start();
      });
    }
  },

  watch: {
    folderId: function (newVal, oldVal) {
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
    ...mapState(["selectedDocumentsHome", "sortHome", "previousLevels"]), // generate vuex computed getter
    ...mapGetters(["getCurrentFolder"]),
  },

  methods: {
    computeFolderUrlPath: function (folderId = null) {
      if (this.previousLevels.length > 0) {
        let s = this.previousLevels.map((e) => e.name);

        if (folderId) {
          s.push(folderId);
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
        this.$store.commit("resetPreviousLevels");
      }
      this.updateFolders(folder);
      this.updateDocuments();
    },

    navigateToFolder: function (folder) {
      if (folder) this.$store.commit("appendNewLevel", folder);
      this.$router.push({
        path: "/home/" + this.computeFolderUrlPath(folder.id),
      });
    },

    changeToPreviousFolder: function () {
      this.$store.commit("removeCurrentLevel");
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
          this.$store.commit("setPreviousLevels", response.data.paths);
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
          this.mixinAlert(this.$t("Could not open this folder"), true);
        });
    },

    documentsCreatedExtended: function (event) {
      const doc = event.doc;
      // Only add document to interface if we are in the same folder, this should allow the user to navigate while uploading
      if (this.folderId) {
        if (parseInt(this.folderId, 10) === doc.ftl_folder) {
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

    updateFolders: function (folder = null) {
      const vi = this;
      let qs = "";

      if (folder) {
        if ("has_descendant" in folder && folder.has_descendant === false) {
          // Avoid doing an API request when we know there are no descendant
          vi.folders = [];
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
          vi.mixinAlert(this.$t("Unable to refresh folders list"), true)
        );
    },

    renameDoc: function (doc) {
      this.currentRenameDoc = doc;
      this.$bvModal.show("modal-rename-document-h");
    },

    documentsCreated: function (event) {
      const doc = event.doc;
      this.docs.unshift(doc);
      this.count++;
    },

    folderCreated: function (folder) {
      folder.highlightAnimation = true;
      this.folders.unshift(folder);
    },

    folderDeleted: function (event) {
      const folderIndex = this._getFolderIndexFromId(event.folder.id);
      this.folders.splice(folderIndex, 1);
    },

    folderUpdated: function (event) {
      const folder = event.folder;
      const folderIndex = this._getFolderIndexFromId(folder.id);
      this.$set(this.folders, folderIndex, folder); // to be reactive, see https://vuejs.org/v2/guide/list.html#Caveats
    },

    _getFolderIndexFromId(folderId) {
      return this.folders.findIndex((x) => x.id === folderId);
    },
  },
};
</script>

<style scoped lang="scss">
@import "~bootstrap/scss/_functions.scss";
@import "~bootstrap/scss/_variables.scss";
@import "~bootstrap/scss/_mixins.scss";

#documents-list {
  min-height: 400px;
}

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

#document-drop-label {
  font-size: 1.2em;
  color: map_get($theme-colors, "light-gray");
  img {
    width: 200px;
    filter: drop-shadow(0 0 1px rgba(0, 0, 0, 0.2));
  }
}

#documents-sort {
  float: right;
  margin-top: 0 !important;
  margin-right: 0 !important;

  ::v-deep .btn {
    padding-right: 0 !important;
    border-right: none !important;
  }
}

/* Hack to fix the driver.js tour highlight for search input (this is a driver,js class)*/
.driver-fix-stacking {
  position: relative !important;
}

.documents-list-dragged-hover {
  background: adjust_color(map_get($theme-colors, "active"), $alpha: -0.7);
  ::v-deep * {
    pointer-events: none;
  }
  ::v-deep .card {
    opacity: 0.3;
  }
}

.driver-popover-title {
  color: map_get($theme-colors, "primary");
}
</style>
