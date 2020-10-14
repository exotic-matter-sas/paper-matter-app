<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <!-- Pdf viewer popup -->
  <b-modal
    id="document-viewer"
    class="px-0"
    hide-footer
    centered
    @hidden="closeDocument"
  >
    <template slot="modal-header">
      <b-container>
        <h5 class="modal-title">
          <b-link
            id="document-parent-folder"
            class="float-left d-none d-md-block"
            :to="parentFolder.to"
            :title="path.map((v) => v.text).join('/')"
          >
            <font-awesome-icon icon="folder" />
            <font-awesome-icon icon="folder-open" class="d-none" />
            {{ parentFolder.text }}
          </b-link>
          <div
            id="document-title-separator"
            class="float-left d-none d-md-block"
          >
            /
          </div>
          <div
            id="document-title"
            class="float-left pl-0"
            :title="currentOpenDoc.title + currentOpenDoc.ext"
          >
            <span>{{ currentOpenDoc.title }}</span>
            <small>{{ currentOpenDoc.ext }}</small>
          </div>
          <b-button
            id="rename-document"
            class="float-left"
            v-b-modal="'modal-rename-document-dp'"
            variant="link"
          >
            <font-awesome-icon
              size="sm"
              icon="pen"
              :title="$t('Rename document')"
            />
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

        <b-dropdown
          id="documents-actions-small"
          class="float-right d-xl-none"
          variant="primary"
          :text="$t('Actions')"
          right
        >
          <b-dropdown-item :href="currentOpenDoc.download_url" target="_blank">
            <font-awesome-icon :icon="getDownloadIcon" />
            <span>{{ $t("Download") }}</span>
          </b-dropdown-item>
          <b-dropdown-item
            :href="currentOpenDoc.download_url + `/doc`"
            target="_blank"
          >
            <font-awesome-icon icon="external-link-alt" />
            <span>{{ $t("Open") }}</span>
          </b-dropdown-item>
          <b-dropdown-divider></b-dropdown-divider>
          <b-dropdown-item
            link-class="text-primary"
            v-b-modal="'modal-document-sharing-dp'"
          >
            <font-awesome-icon
              :icon="currentOpenDoc.is_shared ? 'link' : 'share'"
            />
            <span>
              {{ shareButtonText }}
            </span>
          </b-dropdown-item>
          <b-dropdown-item
            link-class="text-primary"
            @click.prevent="noteToggled = true"
          >
            <font-awesome-icon icon="edit" />
            <span v-if="currentOpenDoc.note === ''">{{ $t("Add note") }}</span>
            <span v-else>{{ $t("Show note") }}</span>
          </b-dropdown-item>
          <b-dropdown-item
            link-class="text-primary"
            v-b-modal="'modal-move-document-dp'"
          >
            <font-awesome-icon icon="arrow-right" />
            <span>{{ $t("Move") }}</span>
          </b-dropdown-item>
          <b-dropdown-item
            class="d-block d-md-none"
            link-class="text-primary"
            :to="parentFolder.to"
          >
            <font-awesome-icon icon="folder-open" />
            <span>{{ $t("Open location") }}</span>
          </b-dropdown-item>
          <b-dropdown-divider></b-dropdown-divider>
          <b-dropdown-item
            link-class="text-danger"
            v-b-modal="'modal-delete-document-dp'"
          >
            <font-awesome-icon icon="trash" />
            <span>{{ $t("Delete") }}</span>
          </b-dropdown-item>
          <b-dropdown-divider></b-dropdown-divider>
          <b-dropdown-form form-class="px-3">
            <b-form-checkbox
              v-model="forcePDFJS"
              name="check-forcePDFJS"
              switch
            >
              {{ $t("Alt. viewer") }}
            </b-form-checkbox>
          </b-dropdown-form>
        </b-dropdown>
      </b-container>
    </template>
    <b-container id="document-viewer-body" class="h-100 px-0" fluid>
      <b-row class="h-100" no-gutters>
        <b-col v-if="currentOpenDoc.type === 'application/pdf' && !isIOS">
          <b-row class="h-100" no-gutters id="viewer-pdf">
            <div id="pdf-embed-container" class="col border-0"></div>
          </b-row>
        </b-col>
        <b-col v-else id="viewer-disabled" class="d-flex align-items-center">
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
        <b-col
          xl="3"
          class="d-none d-xl-block"
          :class="{ 'mobile-note-toggled': noteToggled }"
        >
          <b-row id="documents-actions-big" class="px-3 d-none d-xl-block">
            <b-col class="pt-3 px-3">
              <b-dropdown
                id="download-document"
                class="mr-1 mb-2"
                right
                split
                :split-href="currentOpenDoc.download_url"
              >
                <template v-slot:button-content>
                  <font-awesome-icon :icon="getDownloadIcon" />
                  {{ $t("Download") }}
                </template>
                <b-dropdown-item
                  :href="currentOpenDoc.download_url + `/doc`"
                  target="_blank"
                  id="open-document"
                >
                  <font-awesome-icon icon="external-link-alt" />
                  <span>{{ $t("Open") }}</span>
                </b-dropdown-item>
              </b-dropdown>

              <span class="text-nowrap">
                <b-button
                  id="share-document"
                  class="mr-1 mb-2"
                  variant="primary"
                  v-b-modal="'modal-document-sharing-dp'"
                >
                  <font-awesome-icon
                    :icon="currentOpenDoc.is_shared ? 'link' : 'share'"
                  />
                  {{ shareButtonText }}
                </b-button>

                <b-button
                  id="move-document"
                  class="mr-1 mb-2"
                  variant="primary"
                  v-b-modal="'modal-move-document-dp'"
                >
                  <font-awesome-icon icon="arrow-right" />
                  {{ $t("Move") }}
                </b-button>
              </span>

              <hr class="border-0 m-0" />

              <b-button
                id="delete-document"
                class="mr-1 mb-1"
                variant="outline-danger"
                v-b-modal="'modal-delete-document-dp'"
              >
                <font-awesome-icon icon="trash" />
                {{ $t("Delete") }}
              </b-button>

              <hr />
            </b-col>
          </b-row>

          <b-row class="px-3">
            <b-col class="px-3 py-2 py-xl-0">
              <FTLNote
                v-if="currentOpenDoc.pid"
                :doc="currentOpenDoc"
                @event-document-note-edited="documentNoteUpdated"
                @event-close-note="noteToggled = false"
              />
              <hr />
            </b-col>
          </b-row>

          <b-row class="px-3 d-d">
            <b-col class="px-3">
              <b-form-checkbox
                id="toggle-compat-viewer"
                v-model="forcePDFJS"
                name="check-forcePDFJS"
                switch
              >
                {{ $t("Use alternative PDF viewer") }}
              </b-form-checkbox>
            </b-col>
          </b-row>
        </b-col>
      </b-row>
    </b-container>

    <FTLMoveDocuments
      modal-id="modal-move-document-dp"
      :docs="[currentOpenDoc]"
      @event-document-moved="documentMoved"
    />

    <FTLRenameDocument
      modal-id="modal-rename-document-dp"
      :doc="currentOpenDoc"
      @event-document-renamed="documentRenamed"
    />

    <FTLDeleteDocuments
      modal-id="modal-delete-document-dp"
      :docs="[currentOpenDoc]"
      @event-document-deleted="documentDeleted"
    />

    <FTLDocumentSharing
      modal-id="modal-document-sharing-dp"
      :doc="currentOpenDoc"
      @event-document-shared="documentShared(true)"
      @event-document-unshared="documentShared(false)"
    />
  </b-modal>
</template>

<i18n>
  fr:
    Rename document: Renommer le document
    Viewer not available on this device, open the document instead.: Visualisateur indisponible pour cet appareil,
      ouvrez le document à la place.
    Viewer not available for this document type, open the document instead.: Visualisateur indisponible pour ce type de
      document, ouvrez le document à la place.
    Open: Ouvrir
    Print: Imprimer
    Open document in a new tab: Ouvrir le document dans un nouvel onglet
    Thumbnail updated: Miniature mis à jour
    Unable to create thumbnail: Erreur lors de la génération de la miniature
    Unable to show document: Erreur lors de l'affichage du document
    Sharing: Partage
    Download: Télécharger
    Share: Partager
    Move: Déplacer
    Delete: Supprimer
    Show note: Voir la note
    Add note: Annoter
    Open location: Dossier parent
    Alt. viewer: Visionneuse alternative
    Use alternative PDF viewer: Utiliser une visionneuse PDF alternative
</i18n>

<script>
import axios from "axios";
import PDFObject from "pdfobject";
import FTLMoveDocuments from "@/components/FTLMoveDocuments";
import FTLRenameDocument from "@/components/FTLRenameDocument";
import FTLDeleteDocuments from "@/components/FTLDeleteDocuments";
import FTLThumbnailGenMixin from "@/components/FTLThumbnailGenMixin";
import FTLNote from "@/components/FTLNote";
import FTLDocumentSharing from "@/components/FTLDocumentSharing";

export default {
  name: "FTLDocumentPanel",
  mixins: [FTLThumbnailGenMixin],

  components: {
    FTLMoveDocuments,
    FTLRenameDocument,
    FTLDeleteDocuments,
    FTLNote,
    FTLDocumentSharing,
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
      icons: {
        "application/pdf": "file-pdf",
        "text/plain": "file-alt",
        "application/rtf": "file-alt",
        "application/msword": "file-word",
        "application/vnd.ms-excel": "file-excel",
        "application/vnd.ms-powerpoint": "file-powerpoint",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
          "file-word",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
          "file-excel",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation":
          "file-powerpoint",
      },
      noteToggled: false,
      forcePDFJS: false,
    };
  },

  mounted() {
    if (localStorage.forcepdfjs) {
      // Convert string "true" as stored in localstorage to boolean
      this.forcePDFJS = JSON.parse(localStorage.forcepdfjs);
    }
    this.openDocument();
  },

  computed: {
    getDownloadIcon: function () {
      if (this.currentOpenDoc.type in this.icons) {
        return this.icons[this.currentOpenDoc.type];
      } else {
        return "file";
      }
    },
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
    parentFolder: function () {
      if (this.path.length > 0) {
        return this.path.slice(-1)[0];
      } else {
        return { text: this.$t("Root"), to: { name: "home" } };
      }
    },
    shareButtonText: function () {
      return this.currentOpenDoc.is_shared
        ? this.$t("Sharing")
        : this.$t("Share");
    },
  },

  watch: {
    forcePDFJS: function (newVal, oldVal) {
      localStorage.forcepdfjs = newVal;
      if (this.currentOpenDoc.pid) {
        this.embedPDF();
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
          this.$nextTick().then(() => this.embedPDF());

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

    embedPDF: function () {
      if (this.currentOpenDoc.download_url) {
        let options = {
          PDFJS_URL: "/assets/pdfjs/web/viewer.html",
          supportRedirect: true,
          forcePDFJS: this.forcePDFJS,
          pdfOpenParams: {
            pagemode: "none",
            search: this.search,
          },
        };
        PDFObject.embed(
          this.currentOpenDoc.download_url + "/open",
          "#pdf-embed-container",
          options
        );
      }
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

    documentShared: function (val) {
      this.currentOpenDoc.is_shared = val;
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

<style scoped lang="scss">
@import "~bootstrap/scss/_functions.scss";
@import "~bootstrap/scss/_variables.scss";
@import "~bootstrap/scss/_mixins.scss";

$document-viewer-padding: 2em;

::v-deep #document-viewer .modal-dialog {
  width: 100vw;
  height: 100vh;
  max-width: none;
  margin: 0;

  .modal-content {
    height: 100vh;

    .container {
      max-width: none;
    }

    .modal-header {
      padding-left: 0;
      padding-right: 0;

      .fa-folder {
        width: 1.125em;
      }

      #document-parent-folder,
      #document-title-separator,
      #document-title,
      #rename-document,
      .close {
        display: block;
        padding: 1.25rem;
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
        padding: 1.25rem 1.75rem 1.25rem 0.5rem;
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
    }

    .modal-body {
      padding: 0;

      #viewer-disabled {
        background-color: rgba(0, 0, 0, 0.06);
        text-align: center;
        user-select: none;
      }

      #documents-actions-big hr:last-child {
        margin: 0.75rem 0 0.75rem 0;
      }

      .mobile-note-toggled {
        border-top: 1px solid #dee2e6;
        display: block !important;
        overflow-y: auto;
        overflow-x: hidden;
        animation: slide-up 0.1s linear;
      }
    }

    #document-viewer-body .row {
      flex-direction: column;
    }

    #documents-actions-small a,
    #documents-actions-big a {
      padding-left: 1rem;

      &:active {
        color: white !important;

        &.text-primary {
          background: map_get($theme-colors, "primary");
        }
        &.text-danger {
          background: map_get($theme-colors, "danger");
        }
      }

      span {
        position: absolute;
        left: 0;
        margin-left: 2.75rem;
      }
    }
  }

  #document-viewer #document-viewer-body .row {
    flex-direction: row;
  }
}

@include media-breakpoint-up(md) {
  ::v-deep #document-viewer {
    .modal-dialog {
      padding: $document-viewer-padding;
    }

    .modal-content {
      height: calc(100vh - (#{$document-viewer-padding} * 2)) !important;
    }
  }
}

@include media-breakpoint-up(xl) {
  ::v-deep #document-viewer #document-viewer-body .row {
    flex-direction: row !important;
  }
}
</style>
