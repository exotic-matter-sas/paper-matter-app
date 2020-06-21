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
  >
    <div
      class="card"
      :class="{ selected: $store.getters.FTLDocumentSelected(doc.pid) }"
    >
      <div
        v-if="doc.thumbnail_available"
        class="card-img-top"
        slot="aside"
        :style="{
          'background-image': 'url(' + doc.thumbnail_url + ')',
        }"
        @click.exact="$emit('event-open-doc', doc.pid)"
      ></div>
      <div
        v-else
        class="card-img-top thumb-unavailable"
        slot="aside"
        @click.exact="$emit('event-open-doc', doc.pid)"
      >
        <div class="p-3 doc-icon">
          <font-awesome-icon
            class="d-block mx-auto"
            size="10x"
            :icon="getIcon"
          />
        </div>
      </div>
      <b-card-body>
        <div class="d-flex align-items-center">
          <div class="text-truncate">
            <h4
              class="p-1 card-title document-title rounded"
              :class="{'doc-rename': rename}"
              :title="doc.title + doc.ext + '\n' +  $t('Click to rename')"
              @click.exact="$emit('event-rename-doc', doc)"
              v-b-hover="renameDocument"
            >
              <span>{{ doc.title }}</span>
              <small>{{ doc.ext }}</small>
            </h4>
          </div>
          <font-awesome-icon
            v-show="rename"
            class="ml-auto"
            icon="edit"
          />
          <b-button
            v-show="!rename"
            class="ml-auto download-button"
            variant="secondary"
            size="sm"
            :href="`uploads/${doc.pid}/`"
          >
            <font-awesome-icon :icon="getIcon" :alt="$t('Download')" />
          </b-button>
        </div>
      </b-card-body>
      <b-card-footer :title="$moment(doc.created).format('LLLL')">
        <b-form-checkbox
          :checked="$store.getters.FTLDocumentSelected(doc.pid)"
          @change="toggleSelection"
          :title="$t('Use CTRL + left click for quick selection')"
        />
        <small class="text-muted">{{ $moment(doc.created).fromNow() }}</small>
        <div
          v-if="!doc.is_processed && !timeout_spinner"
          class="spinner-border spinner-border-sm text-primary"
          role="status"
          aria-hidden="true"
          :title="$t('Processing document, it cannot be searched yet.')"
        ></div>
      </b-card-footer>
    </div>
  </b-col>
</template>

<i18n>
  fr:
    Use CTRL + left click for quick selection: Utiliser CTRL + clic gauche pour une sélection rapide
    Processing document, it cannot be searched yet.: Document en cours d'indexation, il ne peut pas être recherché.
</i18n>

<script>
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
  },

  methods: {
    openDoc: function () {
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

    renameDocument: function (hovered) {
      this.rename = hovered;
    },
  },
};
</script>

<style scoped lang="scss">
.document-title {
  color: map_get($theme-colors, "primary");
  border: 1px solid transparent;
}

.card {
  border-color: rgba(0, 0, 0, 0.25);
  border-radius: calc(0.25rem - 1px);

  &:hover {
    border-color: map_get($theme-colors, "primary");
  }
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
  text-align: center;
  padding: 0.5rem 0.75rem;
  font-style: italic;

  .custom-checkbox {
    position: absolute;
  }

  small {
    &::first-letter {
      text-transform: uppercase;
    }

    display: inline-block;
    vertical-align: 0.13rem;
  }

  .spinner-border {
    position: absolute;
    right: 0.75rem;
    bottom: 0.75rem;
  }
}

.doc-icon {
  opacity: 0.1;
}

.doc-rename {
  cursor: text;
  border-color: map_get($theme-colors, "secondary");
}
</style>
