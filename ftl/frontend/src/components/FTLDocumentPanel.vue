<template>
  <!-- Pdf viewer popup -->
  <b-modal id="document-viewer"
           hide-footer
           centered
           @hidden="closeDocument">
    <template slot="modal-header">
      <b-container>
        <b-row align-v="center">
          <b-col>
            <h5 class="d-inline modal-title">{{ currentOpenDoc.title }}</h5>
            <b-button id="rename-document" v-b-modal="'modal-rename-document'" variant="link">
              <font-awesome-icon icon="edit" :title="$_('Rename document')"/>
            </b-button>
          </b-col>
          <b-col>
            <button @click="$bvModal.hide('document-viewer')" type="button" aria-label="Close" class="close">×
            </button>
          </b-col>
        </b-row>
      </b-container>
    </template>
    <b-container class="h-100" fluid>
      <b-row class="h-100">
        <b-col md="8">
          <div v-if="supportInlinePDF" class="h-100 embed-responsive doc-pdf" id="pdfviewer">
            <!--PDF.js viewer-->
          </div>
          <div v-else>
            <span class="text-muted">
              {{ $_('Viewer not available on this device, open the document instead.') }}
            </span>
          </div>
        </b-col>
        <b-col>
          <b-row>
            <b-col class="my-3">
              <b-button class="mx-2" variant="primary" :href="`/app/uploads/` + currentOpenDoc.pid + `/doc.pdf`"
                        target="_blank">
                {{ $_('Open PDF')}}
              </b-button>
              <b-button id="move-document" variant="secondary" v-b-modal="'modal-move-document'">Move</b-button>
            </b-col>
          </b-row>
          <b-row>
            <b-col>
              <hr/>
              <FTLNote v-if="currentOpenDoc.pid" :doc="currentOpenDoc"
                       @event-document-note-edited="documentNoteUpdated"/>
            </b-col>
          </b-row>
        </b-col>
      </b-row>
    </b-container>

    <FTLMoveDocuments
      v-if="currentOpenDoc"
      id="modal-move-document"
      :docs="[currentOpenDoc]"
      @event-document-moved="$emit('event-document-moved', $event)"/>

    <FTLRenameDocument
      v-if="currentOpenDoc.pid"
      :doc="currentOpenDoc"
      @event-document-renamed="documentRenamed"/>
  </b-modal>
</template>
<script>
  import axios from 'axios';
  import PDFObject from "pdfobject";
  import FTLMoveDocuments from "@/components/FTLMoveDocuments";
  import FTLRenameDocument from "@/components/FTLRenameDocument";
  import FTLThumbnailGenMixin from "@/components/FTLThumbnailGenMixin";
  import FTLNote from "@/components/FTLNote";

  export default {
    name: "FTLDocumentPanel",
    mixins: [FTLThumbnailGenMixin],

    components: {
      FTLMoveDocuments,
      FTLRenameDocument,
      FTLNote
    },

    props: {
      pid: {
        type: String,
        required: true
      },
      search: {
        type: String,
        required: false
      }
    },

    data() {
      return {
        currentOpenDoc: {},
        publicPath: process.env.BASE_URL,
        supportInlinePDF: PDFObject.supportsPDFs
      }
    },

    mounted() {
      this.openDocument();
    },

    methods: {
      openDocument: function () {
        const pdf_options = {
          forcePDFJS: true,
          assumptionMode: false,
          PDFJS_URL: "/assets/pdfjs/web/viewer.html"
        };

        this.$bvModal.show('document-viewer');

        axios
          .get('/app/api/v1/documents/' + this.pid)
          .then(response => {
            this.currentOpenDoc = response.data;

            if (this.supportInlinePDF) {
              PDFObject.embed('/app/uploads/' + this.currentOpenDoc.pid + '/doc.pdf',
                "#pdfviewer",
                {
                  ...pdf_options, ...{
                    pdfOpenParams: {
                      pagemode: "none",
                      search: this.search
                    },
                  }
                }
              );
            }

            if (!response.data.thumbnail_available) {
              this.createThumbnailForDocument(this.currentOpenDoc)
                .then(response => {
                  this.mixinAlert("Thumbnail updated!");
                })
                .catch(error => this.mixinAlert("Unable to create thumbnail", true));
            }
          })
          .catch(error => {
            this.mixinAlert("Unable to show document.", true)
          });
      },

      documentRenamed: function (event) {
        this.currentOpenDoc = event.doc;
        this.$emit('event-document-renamed', event)
      },

      documentNoteUpdated: function (event) {
        this.currentOpenDoc = event.doc;
      },

      closeDocument: function () {
        this.currentOpenDoc = {};
        this.$bvModal.hide('document-viewer');
        this.$emit('event-document-panel-closed');
        this.$router.push({path: this.$route.path});
      }
    }
  }
</script>
<style lang="scss">
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

    .modal-title {
      vertical-align: middle;
    }

    .modal-content {
      height: calc(100vh - (#{$document-viewer-padding} * 2));
    }
  }
</style>
