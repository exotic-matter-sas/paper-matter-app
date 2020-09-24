<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <b-col
    cols="12"
    mb="4"
    sm="6"
    md="4"
    lg="3"
    xl="2"
    class="mb-3 document-thumbnail"
    :id="doc.pid"
    @click.ctrl="toggleSelection"
    :draggable="selectedDocumentsHome.length === 0"
    v-on:dragstart="dragstart"
  >
    <div
      class="card"
      :class="{
        selected: $store.getters.FTLDocumentSelected(doc.pid),
        'last-selected':
          isOpened && !$store.getters.FTLDocumentSelected(doc.pid),
      }"
    >
      <div
        v-if="doc.thumbnail_available"
        class="card-img-top"
        slot="aside"
        :style="{
          'background-image': 'url(' + doc.thumbnail_url + ')',
        }"
        @click.exact="openDoc"
      ></div>
      <div
        v-else
        class="card-img-top thumb-unavailable"
        slot="aside"
        @click.exact="openDoc"
      >
        <div class="p-3 doc-icon">
          <font-awesome-icon
            class="d-block mx-auto"
            size="10x"
            :icon="getIcon"
          />
        </div>
      </div>
      <b-form-checkbox
        :checked="$store.getters.FTLDocumentSelected(doc.pid)"
        @change="toggleSelection"
        size="lg"
        class="position-absolute checkbox-overlay-thumb"
      />
      <b-card-body>
        <div class="d-flex align-items-center">
          <div class="text-truncate">
            <h4
              class="py-1 pr-1 card-title document-title rounded"
              :class="{ 'doc-rename': rename }"
              :title="doc.title + doc.ext + '\n' + $t('Click to rename')"
              @click.exact="$emit('event-rename-doc', doc)"
              v-b-hover="renameDocument"
            >
              <span>{{ doc.title }}</span>
              <small>{{ doc.ext }}</small>
            </h4>
          </div>
          <font-awesome-icon v-show="rename" class="ml-auto" icon="pen" />
          <b-button
            v-show="!rename"
            class="ml-auto download-button"
            variant="secondary"
            size="sm"
            :href="doc.download_url"
            :title="$t('Download document')"
          >
            <font-awesome-icon :icon="getIcon" :alt="$t('Download')" />
          </b-button>
        </div>
      </b-card-body>
      <b-card-footer class="p-0">
        <div class="d-flex align-items-center justify-content-between p-2">
          <small
            class="ml-1 text-muted text-wrap"
            :title="$moment(doc.created).format('LLLL')"
            >{{ $moment(doc.created).fromNow() }}</small
          >
          <div
            v-if="!doc.is_processed && !timeout_spinner"
            class="mr-1 spinner-border spinner-border-sm text-primary"
            role="status"
            aria-hidden="true"
            :title="$t('Processing document, it will be searchable soon.')"
          ></div>
        </div>
      </b-card-footer>
    </div>
  </b-col>
</template>

<i18n>
  fr:
    You can also use CTRL + left click to select document: Vous pouvez aussi utiliser CTRL + clic gauche pour sélectionner le document
    Processing document, it will be searchable soon.: Document en cours d'indexation, il pourra bientôt être recherché.
    Click to rename: Cliquer pour renommer
    Drag to folder to move document: Saisir pour déplacer le document
    Download document: Télécharger le document
</i18n>

<script>
import { mapState } from "vuex";

export default {
  props: {
    doc: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      timer: null,
      timeout_spinner: false,
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
      rename: false,
      opened: false,
    };
  },

  created() {
    if (this.doc.is_processed === false) {
      this.timer = setTimeout(this.stop_spinner, 300000);
    }
  },

  beforeDestroy() {
    if (this.timer) {
      clearTimeout(this.timer);
    }
  },

  computed: {
    getIcon: function () {
      if (this.doc.type in this.icons) {
        return this.icons[this.doc.type];
      } else {
        return "file";
      }
    },

    isOpened: function () {
      return this.doc.pid === this.lastOpenedDocument;
    },

    ...mapState(["selectedDocumentsHome", "lastOpenedDocument"]),
  },

  methods: {
    openDoc: function () {
      this.$store.commit("setLastOpenedDocument", this.doc.pid);
      this.$emit("event-open-doc", this.doc.pid);
    },

    toggleSelection: function () {
      if (this.$store.getters.FTLDocumentSelected(this.doc.pid)) {
        this.$store.commit("unselectDocument", this.doc);
      } else {
        this.$store.commit("selectDocuments", [this.doc]);
      }
    },

    stop_spinner: function () {
      this.timeout_spinner = true;
    },

    dragstart: function (event) {
      event.dataTransfer.setData("application/ftl-pid", this.doc.pid); // Only string data can be passed
      // Remove drag ghost image
      const img = new Image();
      img.src =
        "data:image/gif;base64,R0lGODlhAQABAIAAAAUEBAAAACwAAAAAAQABAAACAkQBADs=";
      event.dataTransfer.setDragImage(img, 0, 0);
    },

    renameDocument: function (hovered) {
      this.rename = hovered;
    },
  },
};
</script>

<style scoped lang="scss">
@import "~bootstrap/scss/_functions.scss";
@import "~bootstrap/scss/_variables.scss";
@import "~bootstrap/scss/_mixins.scss";

.document-title {
  color: map_get($theme-colors, "primary");
  border: 1px solid transparent;
  transition: padding 0.1s linear;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;

  &:hover {
    padding-left: 0.25rem;
  }
}

.card {
  border-color: rgba(0, 0, 0, 0.25);
  border-radius: calc(0.25rem - 1px);

  &:hover {
    border-color: map_get($theme-colors, "primary");

    ::v-deep
      .custom-checkbox.b-custom-control-lg
      .custom-control-label::before {
      border-color: map_get($theme-colors, "primary");
    }
  }
}

.last-selected {
  border-color: map_get($theme-colors, "active");
}

.selected {
  border-color: transparent;
  box-shadow: 0 0 0 2px map_get($theme-colors, "active");

  &:hover {
    border-color: transparent;
    box-shadow: 0 0 0 2px map_get($theme-colors, "primary");
  }
}

.card-img-top {
  height: 200px;
  box-shadow: inset 0 -10px 30px -30px #0a0a0a;
  background-repeat: no-repeat;
  background-size: cover;
  transition: background-position 1.2s cubic-bezier(0.68, -0.55, 0.27, 1.55) 1s,
    box-shadow 1.2s ease-in-out 1s;
  cursor: pointer;
  border-bottom: 1px solid rgba(0, 0, 0, 0.125);
}

.card-img-top.thumb-unavailable {
  background-color: rgba(0, 0, 0, 0.03);
}

.card-title {
  cursor: pointer;
  font-size: 1.1rem;
  margin-bottom: 0;
}

.card-img-top:not(.thumb-unavailable):hover {
  background-position: bottom;
  box-shadow: inset 0 10px 30px -30px #0a0a0a;
}

.card-body {
  padding: 0.75rem;
}

.card-footer {
  font-style: italic;

  small {
    &::first-letter {
      text-transform: uppercase;
    }
  }
}

.doc-icon {
  opacity: 0.1;
}

.doc-rename {
  cursor: text;
  border-color: map_get($theme-colors, "secondary");
}

.checkbox-overlay-thumb {
  top: 0.25rem;
  right: 0;
}
</style>
