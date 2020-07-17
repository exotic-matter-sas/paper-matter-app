<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <!-- Pdf viewer popup -->
  <b-modal
    id="document-viewer"
    hide-footer
    centered
    @hidden="closeDocument"
    @hide="viewerPdfJsUrl = null"
  >
    <template slot="modal-header">
      <b-container>
        <h5 class="modal-title">
          <b-link
            id="document-parent-folder"
            class="float-left"
            :to="parent_folder.to"
            :title="path.map((v) => v.text).join('/')"
          >
            <font-awesome-icon icon="folder" />
            <font-awesome-icon icon="folder-open" class="d-none" />
            {{ parent_folder.text }}
          </b-link>
          <div id="document-title-separator" class="float-left">
            /
          </div>
          <div
            id="document-title"
            class="float-left"
            :title="currentOpenDoc.title + currentOpenDoc.ext"
          >
            <span>{{ currentOpenDoc.title }}</span>
            <small>{{ currentOpenDoc.ext }}</small>
          </div>
          <b-button
            id="rename-document"
            class="float-left"
            v-b-modal="'modal-rename-document'"
            variant="link"
          >
            <font-awesome-icon icon="edit" :title="$t('Rename document')" />
          </b-button>
        </h5>

        <button
          @click.prevent="$bvModal.hide('document-viewer')"
          type="button"
          aria-label="Close"
          class="close"
        >
          ×
        </button>
      </b-container>
    </template>
    <b-container class="h-100" fluid>
      <b-row class="h-100">
        <b-col
          md="8"
          v-if="currentOpenDoc.type === 'application/pdf' && !isIOS"
        >
          <div class="h-100 embed-responsive doc-pdf" id="pdfviewer">
            <iframe
              v-if="viewerPdfJsUrl"
              class="embed-responsive-item"
              :src="viewerPdfJsUrl"
            >
            </iframe>
          </div>
        </b-col>
        <b-col
          md="6"
          v-else
          id="viewer-disabled"
          class="d-flex align-items-center"
        >
          <b-row class="m-2 w-100 text-muted font-italic">
            <b-col v-if="isIOS">
              {{
                $t(
                  "Viewer not available on this device, open the document instead."
                )
              }}
            </b-col>
            <b-col v-else class="text-muted">
              {{
                $t(
                  "Viewer not available for this document type, open the document instead."
                )
              }}
            </b-col>
          </b-row>
        </b-col>
        <b-col>
          <b-row>
            <b-col class="mb-1">
              <b-button
                id="open-document"
                class="mx-1 mb-1"
                variant="primary"
                :href="currentOpenDoc.download_url + `/doc`"
                target="_blank"
                :title="$t('Open document in a new tab')"
              >
                {{ $t("Open document") }}
                <font-awesome-icon icon="external-link-alt" size="sm" />
              </b-button>
              <b-button
                id="move-document"
                class="mx-1 mb-1"
                variant="secondary"
                v-b-modal="'modal-move-document'"
              >
                {{ $t("Move") }}
              </b-button>
              <b-button
                id="delete-document"
                class="mx-1 mb-1"
                variant="danger"
                v-b-modal="'modal-delete-document'"
              >
                {{ $t("Delete") }}
              </b-button>
            </b-col>
          </b-row>
          <b-row>
            <b-col>
              <hr />
              <FTLNote
                v-if="currentOpenDoc.pid"
                :doc="currentOpenDoc"
                @event-document-note-edited="documentNoteUpdated"
              />
            </b-col>
          </b-row>
        </b-col>
      </b-row>
    </b-container>

    <FTLMoveDocuments
      v-if="currentOpenDoc.pid"
      id="modal-move-document"
      :docs="[currentOpenDoc]"
      @event-document-moved="documentMoved"
    />

    <FTLRenameDocument
      v-if="currentOpenDoc.pid"
      :doc="currentOpenDoc"
      @event-document-renamed="documentRenamed"
    />

    <FTLDeleteDocuments
      v-if="currentOpenDoc.pid"
      id="modal-delete-document"
      :docs="[currentOpenDoc]"
      @event-document-deleted="documentDeleted"
    />
  </b-modal>
</template>

<i18n>
  fr:
    Click to rename document: Cliquez pour renommer
    Viewer not available on this device, open the document instead.: Visualisateur indisponible pour cet appareil,
      ouvrez le document à la place.
    Viewer not available for this document type, open the document instead.: Visualisateur indisponible pour ce type de
      document, ouvrez le document à la place.
    Open document: Ouvrir le document
    Open document in a new tab: Ouvrir le document dans un nouvel onglet
    Thumbnail updated: Miniature mis à jour
    Unable to create thumbnail: Erreur lors de la génération de la miniature
    Unable to show document: Erreur lors de l'affichage du document
</i18n>

<script>
import axios from "axios";
import FTLMoveDocuments from "@/components/FTLMoveDocuments";
import FTLRenameDocument from "@/components/FTLRenameDocument";
import FTLDeleteDocuments from "@/components/FTLDeleteDocuments";
import FTLThumbnailGenMixin from "@/components/FTLThumbnailGenMixin";
import FTLNote from "@/components/FTLNote";
import { mapState } from "vuex";

export default {
  name: "FTLDocumentPanel",
  mixins: [FTLThumbnailGenMixin],

  components: {
    FTLMoveDocuments,
    FTLRenameDocument,
    FTLDeleteDocuments,
    FTLNote,
  },

  props: {
    pid: {
      type: String,
      required: true,
    },
    search: {
      type: String,
      required: false,
      default: "",
    },
  },

  data() {
    return {
      currentOpenDoc: { path: [] },
      publicPath: process.env.BASE_URL,
      viewerPdfJsUrl: "",
    };
  },

  mounted() {
    this.openDocument();
  },

  computed: {
    isIOS: function () {
      return /iphone|ipad|ipod/i.test(window.navigator.userAgent.toLowerCase());
    },
    path: function () {
      let _path = this.currentOpenDoc.path.map((v) => {
        return {
          text: v.name,
          to: { path: "/home/" + v.name + "/" + v.id },
        };
      });

      return [{ text: this.$t("Root"), to: { name: "home" } }, ..._path];
    },
    parent_folder: function () {
      if (this.path.length > 0) {
        return this.path.slice(-1)[0];
      } else {
        return { text: this.$t("Root"), to: { name: "home" } };
      }
    },
  },

  methods: {
    openDocument: function () {
      this.$bvModal.show("document-viewer");

      axios
        .get("/app/api/v1/documents/" + this.pid)
        .then((response) => {
          this.currentOpenDoc = response.data;
          this.viewerPdfJsUrl = this.viewerUrl();

          if (
            !response.data.thumbnail_available &&
            response.data.type === "application/pdf"
          ) {
            this.createThumbnailForDocument(this.currentOpenDoc)
              .then((response) => {
                this.mixinAlert(this.$t("Thumbnail updated"));
              })
              .catch((error) =>
                this.mixinAlert(this.$t("Unable to create thumbnail"), true)
              );
          }
        })
        .catch((error) => {
          this.mixinAlert(this.$t("Unable to show document"), true);
        });
    },

    viewerUrl: function () {
      return (
        `/assets/pdfjs/web/viewer.html?r=` +
        new Date().getTime() +
        `&file=` +
        this.currentOpenDoc.download_url +
        `#pagemode=none&search=` +
        this.search
      );
    },

    documentRenamed: function (event) {
      this.currentOpenDoc = event.doc;
      this.$emit("event-document-renamed", event);
    },

    documentMoved: function (event) {
      this.currentOpenDoc = event.doc;
      this.$emit("event-document-moved", event);
    },

    documentNoteUpdated: function (event) {
      this.currentOpenDoc = event.doc;
    },

    documentDeleted: function (event) {
      this.closeDocument();
      this.$emit("event-document-deleted", event);
    },

    closeDocument: function () {
      this.$bvModal.hide("document-viewer");
      this.$emit("event-document-panel-closed", {
        doc: this.currentOpenDoc,
      });
      this.$router.push({ path: this.$route.path }, () => {});
      this.currentOpenDoc = { path: [] };
    },
  },
};
</script>

<style lang="scss">
// Don't use `scoped` on this style because the document viewer is styled from the main app component
$document-viewer-padding: 2em;

#document-viewer {
  .container {
    max-width: none;
  }

  .modal-dialog {
    width: 100vw;
    height: 100vh;
    max-width: none;
    padding: $document-viewer-padding;
    margin: 0;
  }

  .fa-folder {
    width: 1.125em;
  }

  #document-parent-folder,
  #document-title-separator,
  #document-title,
  #rename-document {
    display: block;
    padding: 1rem;
    margin: -1rem -1rem -1rem auto;
  }

  #document-parent-folder {
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

  #document-title-separator {
    padding: 1rem 0.5rem;
  }

  #document-title {
    max-width: 65%;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  #rename-document {
    font-size: 1.25rem;
    line-height: 1.5;
    border: 0;
    padding-left: 0.5rem;
  }

  .close {
    line-height: 1.25;
  }

  .modal-content {
    height: calc(100vh - (#{$document-viewer-padding} * 2));
  }

  #viewer-disabled {
    background-color: rgba(0, 0, 0, 0.06);
    text-align: center;
    user-select: none;
  }
}
</style>
