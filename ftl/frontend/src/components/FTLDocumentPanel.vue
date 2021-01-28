<!--
  - Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
  - Licensed under the Business Source License. See LICENSE in the project root for license information.
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
      <b-container fluid class="p-0">
        <b-row no-gutters class="flex-nowrap">
          <b-col class="modal-title flex-grow-1">
            <b-row tag="h2" no-gutters class="m-0 flex-nowrap">
              <b-col class="flex-grow-0">
                <div class="text-truncate">
                  <b-link
                    id="document-parent-folder"
                    class="d-none d-md-inline text-nowrap"
                    :to="parentFolder.to"
                    :title="path.map((v) => v.text).join('/')"
                  >
                    <font-awesome-icon icon="folder" />
                    <font-awesome-icon icon="folder-open" class="d-none" />
                    {{ parentFolder.text }}
                  </b-link>
                  <span
                    id="document-title-separator"
                    class="d-none d-md-inline"
                  >
                    /
                  </span>
                  <span :title="currentOpenDoc.title + currentOpenDoc.ext">
                    <span id="document-title">
                      {{ currentOpenDoc.title }}
                    </span>
                    <small id="document-title-extension">{{
                      currentOpenDoc.ext
                    }}</small>
                  </span>
                </div>
              </b-col>
              <b-col class="flex-grow-1">
                <b-button
                  id="rename-document"
                  class="p-0"
                  v-b-modal="'modal-rename-document-dp'"
                  variant="link"
                >
                  <font-awesome-icon
                    size="sm"
                    icon="pen"
                    :title="$t('Rename document')"
                  />
                </b-button>
              </b-col>
            </b-row>
            <b-row no-gutters>
              <b-col class="text-muted font-italic text-truncate pr-2">
                <small class="d-none d-sm-inline">
                  {{
                    $t("Added on {date}", {
                      date: $moment
                        .parseZone(currentOpenDoc.created)
                        .format("LLLL"),
                    })
                  }}
                </small>
                <small class="d-inline d-sm-none">
                  {{
                    $t("Added on {date}", {
                      date: $moment
                        .parseZone(currentOpenDoc.created)
                        .format("L"),
                    })
                  }}
                </small>
              </b-col>
            </b-row>
          </b-col>
          <b-col class="flex-grow-0 d-flex align-items-center">
            <b-dropdown
              id="documents-actions-small"
              class="d-xl-none"
              variant="primary"
              :text="$t('Actions')"
              right
            >
              <b-dropdown-item
                :href="currentOpenDoc.download_url"
                target="_blank"
              >
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
                <span v-if="currentOpenDoc.note === ''">{{
                  $t("Add note")
                }}</span>
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
              <b-dropdown-item
                link-class="text-primary"
                v-b-modal="'modal-document-reminder-dp'"
              >
                <font-awesome-icon icon="bell" />
                <span>
                  {{
                    $tc(
                      "Reminders | One reminder | Reminders ({count})",
                      currentOpenDoc.reminders_count,
                      {
                        count: currentOpenDoc.reminders_count,
                      }
                    )
                  }}
                </span>
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
              <b-dropdown-form v-if="!useOnlyOfficeViewer" form-class="px-3">
                <b-form-checkbox
                  v-model="forcePDFJS"
                  name="check-forcePDFJS"
                  switch
                >
                  {{ $t("Alt. viewer") }}
                </b-form-checkbox>
              </b-dropdown-form>
            </b-dropdown>
          </b-col>
          <b-col class="flex-grow-0 d-flex">
            <button
              @click.prevent="$bvModal.hide('document-viewer')"
              type="button"
              aria-label="Close"
              class="close"
            >
              ×
            </button>
          </b-col>
        </b-row>
      </b-container>
    </template>

    <b-container id="document-viewer-body" class="px-0" fluid>
      <b-row class="h-100" no-gutters>
        <b-col v-if="currentOpenDoc.type === 'application/pdf' && !isIOS">
          <b-row class="h-100" no-gutters id="viewer-pdf">
            <div id="pdf-embed-container" class="col border-0"></div>
          </b-row>
        </b-col>
        <b-col v-else-if="useOnlyOfficeViewer">
          <b-row class="h-100" no-gutters id="viewer-only-office">
            <div id="onlyoffice-embed-container" class="col border-0"></div>
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
          class="d-none d-xl-block px-3"
          :class="{ 'mobile-note-toggled': noteToggled }"
        >
          <b-row id="documents-actions-big" class="d-none d-xl-block">
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

              <hr class="border-0 m-0" />

              <span>
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

                <b-button
                  id="document-reminder"
                  class="mr-1 mb-2"
                  variant="primary"
                  v-b-modal="'modal-document-reminder-dp'"
                >
                  <font-awesome-icon icon="bell" />
                  {{ $t("Reminders") }}&nbsp;
                  <b-badge
                    v-if="currentOpenDoc.reminders_count > 0"
                    variant="dark"
                  >
                    {{ currentOpenDoc.reminders_count }}
                  </b-badge>
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

          <b-row>
            <b-col class="px-3 py-2 py-xl-0">
              <FTLNote
                v-if="currentOpenDoc.pid"
                :doc="currentOpenDoc"
                @event-document-note-edited="documentNoteUpdated"
                @event-close-note="noteToggled = false"
              />
            </b-col>
          </b-row>

          <b-row v-if="!useOnlyOfficeViewer" class="d-none d-xl-block">
            <b-col class="px-3">
              <hr />
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

    <FTLDocumentReminder
      modal-id="modal-document-reminder-dp"
      :doc="currentOpenDoc"
      @event-document-reminders-updated="documentRemindersUpdated"
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
    Reminders: Rappels
    Reminders | One reminder | Reminders ({count}): Rappels | Un rappel | Rappels ({count})
    Added on {date}: Ajouté le {date}
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
import FTLDocumentReminder from "@/components/FTLDocumentReminder";
import { mapState } from "vuex";

export default {
  name: "FTLDocumentPanel",
  mixins: [FTLThumbnailGenMixin],

  components: {
    FTLDocumentReminder,
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
      this.forcePDFJS = localStorage.forcepdfjs === "true";
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
          to: { path: "/folder/" + v.name + "/" + v.id },
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
    useOnlyOfficeViewer: function () {
      if (this.ftlAccount["only_office_viewer"] === true) {
        return [
          "text/plain",
          "application/rtf",
          "text/rtf",
          "application/msword",
          "application/vnd.ms-excel",
          "application/excel",
          "application/vnd.ms-powerpoint",
          "application/mspowerpoint",
          "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          "application/vnd.openxmlformats-officedocument.presentationml.presentation",
          "application/vnd.oasis.opendocument.text",
          "application/vnd.oasis.opendocument.presentation",
          "application/vnd.oasis.opendocument.spreadsheet",
        ].includes(this.currentOpenDoc.type);
      } else {
        return false;
      }
    },
    ...mapState(["ftlAccount"]), // generate vuex computed getter
  },

  watch: {
    forcePDFJS: function (newVal, oldVal) {
      // Forcing boolean to be stored as string to avoid possible future bug
      // https://stackoverflow.com/questions/3263161/cannot-set-boolean-values-in-localstorage/
      localStorage.forcepdfjs = String(newVal);
      if (this.currentOpenDoc.pid) {
        this.embedDoc();
      }
    },
  },

  methods: {
    openDocument: function () {
      this.$bvModal.show("document-viewer");

      axios
        .get("/app/api/v1/documents/" + this.pid)
        .then((response) => {
          // Using Object.assign to enable reactivity on currentOpenDoc attributs
          this.currentOpenDoc = Object.assign(
            {},
            this.currentOpenDoc,
            response.data
          );
          this.$nextTick().then(() => this.embedDoc());

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

    embedDoc: function () {
      if (this.currentOpenDoc.download_url) {
        if (this.currentOpenDoc.type === "application/pdf") {
          let options = {
            PDFJS_URL: "/assets/pdfjs/web/viewer.html",
            supportRedirect: true,
            forcePDFJS: this.forcePDFJS,
            omitInlineStyles: true,
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
        } else if (this.useOnlyOfficeViewer) {
          new DocsAPI.DocEditor(
            "onlyoffice-embed-container",
            this.currentOpenDoc.only_office_config
          );
        }
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

    documentRemindersUpdated: function (event) {
      this.currentOpenDoc.reminders_count = event.reminders_count;
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
$rename-button-width: 20px;
$rename-button-left-margin: 0.2em;
$rename-button-right-margin: 1em;

::v-deep .pdfobject {
  overflow: auto;
  width: 100%;
  height: 100%;
}

::v-deep .pdfobject-container > div {
  height: 100%;
}

::v-deep #document-viewer .modal-dialog {
  width: 100vw;
  height: 100vh;
  max-width: none;
  margin: 0;
  overflow: hidden;

  .modal-content {
    height: 100vh;

    .container {
      max-width: none;
    }

    .modal-header {
      padding: 0.5rem 1rem;

      .modal-title {
        min-width: 0;

        h2 {
          font-size: 1.25rem;

          .col:first-child {
            padding-right: calc(
              #{$rename-button-width} + #{$rename-button-left-margin} + #{$rename-button-right-margin}
            );
          }

          #document-parent-folder {
            .fa-folder {
              width: 1.125em;
            }

            &:hover {
              .fa-folder {
                display: none !important;
              }

              .fa-folder-open {
                display: inline-block !important;
              }
            }
          }

          #document-title-extension {
            margin-left: -0.2em;
          }

          #rename-document {
            width: $rename-button-width;
            margin-top: -0.1em;
            margin-left: calc(
              (-#{$rename-button-width} - (#{$rename-button-right-margin}))
            );
            font-size: 1.25rem;
            position: absolute; // hack to not increase parent height
          }
        }
      }
    }

    .modal-body {
      display: flex;
      padding: 0;

      #viewer-disabled {
        background-color: rgba(0, 0, 0, 0.06);
        text-align: center;
        user-select: none;
      }

      #pdf-embed-container iframe {
        border: none;
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
