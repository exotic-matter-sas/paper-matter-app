<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <b-row>
    <b-col id="note-title" cols="12" class="mb-1">
      <h6 class="d-inline font-weight-bold">{{ $t("Note") }}</h6>
      <b-button
        v-if="!editing"
        id="edit-note"
        variant="link"
        size="sm"
        @click.prevent="editing = true"
      >
        <font-awesome-icon icon="edit" :title="$t('Edit note')" />
      </b-button>

      <span v-if="editing" class="d-inline d-xl-none">
        <b-button
          class="float-right"
          id="save-note"
          variant="primary"
          size="sm"
          :disabled="doc.note === text"
          @click.prevent="updateNote"
        >
          {{ $t("Save") }}
        </b-button>
        <b-button
          class="float-right"
          variant="link"
          size="sm"
          :disabled="editing === false"
          @click.prevent="cancelUpdate"
        >
          {{ $t("Cancel") }}
        </b-button>
      </span>
      <span v-else>
        <b-button
          class="float-right d-inline d-xl-none"
          variant="secondary"
          size="sm"
          @click.prevent="$emit('event-close-note')"
        >
          {{ $t("Close note") }}
        </b-button>
      </span>
    </b-col>

    <b-col v-if="editing" id="note-form">
      <b-row>
        <b-col>
          <b-tabs content-class="mt-2" small lazy>
            <b-tab :title="$t('Edition')" active>
              <b-form-textarea
                id="note-textarea"
                v-model="text"
                :placeholder="$t('Example note')"
                max-rows="10"
              >
              </b-form-textarea>
            </b-tab>
            <b-tab :title="$t('Preview')">
              <div id="note-preview">
                <span v-html="getNoteMarkdownSanitized"></span>
              </div>
            </b-tab>
          </b-tabs>
        </b-col>
      </b-row>
      <b-row id="note-toolbar" class="mt-2" align-v="center">
        <b-col>
          <div id="note-tip" class="d-none d-xl-block">
            <a
              v-if="doc.note === text"
              class="text-muted"
              :title="$t('Markdown syntax supported')"
              href="https://guides.github.com/features/mastering-markdown/#examples"
              target="_blank"
            >
              <font-awesome-icon
                :icon="['fab', 'markdown']"
                rel="Markdown logo"
              />&nbsp;
              {{ $t("supported") }}
            </a>
            <span v-else class="highlight">
              <font-awesome-icon icon="exclamation-circle" />
              {{ $t("unsaved note") }}
            </span>
          </div>
        </b-col>
        <b-col class="text-right d-none d-xl-block">
          <b-button
            variant="link"
            size="sm"
            :disabled="editing === false"
            @click.prevent="cancelUpdate"
          >
            {{ $t("Cancel") }}
          </b-button>
          <b-button
            id="save-note"
            variant="primary"
            size="sm"
            :disabled="doc.note === text"
            @click.prevent="updateNote"
          >
            {{ $t("Save") }}
          </b-button>
        </b-col>
      </b-row>
    </b-col>

    <b-col v-else-if="doc.note">
      <div id="note"><span v-html="getNoteMarkdownSanitized"></span></div>
    </b-col>

    <b-col v-else>
      <span class="text-muted font-italic">{{ $t("No note set") }}</span>
    </b-col>
  </b-row>
</template>

<i18n>
  fr:
    Note: Note
    Edit note: Éditer note
    Edition: Édition
    Example note: Note d'exemple
    Preview: Prévisualisation
    Markdown syntax supported: Syntaxe Markdown supportée
    supported: supportée
    unsaved note: note non sauvegardée
    No note set: Aucune note définie
    Could not save note: La note n'a pu être sauvegardée
</i18n>

<script>
import marked from "marked";
import dompurify from "dompurify";
import axios from "axios";
import { axiosConfig, markedConfig } from "@/constants";

export default {
  name: "FTLNote",

  props: {
    doc: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      editing: false,
      text: this.doc.note,
    };
  },

  computed: {
    getNoteMarkdownSanitized: function () {
      const markdownHtml = marked(this.text, markedConfig);
      return dompurify.sanitize(markdownHtml);
    },
  },

  methods: {
    updateNote: function () {
      this.editing = false;

      let body = {
        note: this.text,
      };

      axios
        .patch("/app/api/v1/documents/" + this.doc.pid, body, axiosConfig)
        .then((response) => {
          this.$emit("event-document-note-edited", {
            doc: response.data,
          });
        })
        .catch((error) => {
          this.mixinAlert(this.$t("Could not save note"), true);
        });
    },

    cancelUpdate: function () {
      this.editing = false;
      this.text = this.doc.note;
    },
  },
};
</script>

<style scoped lang="scss">
@import "~bootstrap/scss/_functions.scss";
@import "~bootstrap/scss/_variables.scss";
@import "~bootstrap/scss/_mixins.scss";

#note-title {
  // to avoid #note-form visible behind title during animation
  background: white;
  z-index: $zindex-dropdown;

  .btn {
    // to avoid wobbly UI when button disappear
    padding-top: 0;
    padding-bottom: 0;
  }
}

#note {
  overflow: auto;
  max-height: 200px;
}

#note-tip {
  font-size: 0.9rem;
}

#note-form {
  animation: slide-down 0.2s linear;

  textarea, #note-preview {
    max-height: 200px;
    overflow-y: scroll;
  }
}
</style>
