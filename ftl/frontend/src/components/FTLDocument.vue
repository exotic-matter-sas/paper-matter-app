<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <b-col cols="12" mb="4" sm="6" md="4" lg="3" xl="2" class="mb-3 document-thumbnail" :id="doc.pid"
         @click.ctrl="toggleSelection">
    <div class="card" :class="{'selected': $store.getters.FTLDocumentSelected(doc.pid)}">
      <div class="card-img-top" slot="aside"
           :style="{'background-image': 'url(' + doc.thumbnail_url + ')'}"
           @click.exact="$emit('event-open-doc', doc.pid)"></div>
      <b-card-body>
        <b-button class="float-right" variant="secondary" size="sm" :href="'uploads/' + doc.pid">
          <font-awesome-icon icon="file-download" :alt="$t('Download')"/>
        </b-button>
        <b-card-title class="text-truncate document-title"
                      @click.exact="$emit('event-open-doc', doc.pid)"
        >
          <span :title="doc.title">{{ doc.title }}</span>
        </b-card-title>
      </b-card-body>
      <b-card-footer :title="$moment(doc.created).format('LLLL')">
        <b-form-checkbox :checked="$store.getters.FTLDocumentSelected(doc.pid)" @change="toggleSelection"
                         :title="$t('Use CTRL + left click for quick selection')"/>
        <small class="text-muted">{{ $moment(doc.created).fromNow() }}</small>
        <div v-if="!doc.is_processed && !timeout_spinner" class="spinner-border spinner-border-sm text-primary"
             role="status" aria-hidden="true" :title="$t('Processing document, it cannot be searched yet.')"></div>
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
        required: true
      }
    },

    data() {
      return {
        timer: null,
        timeout_spinner: false
      }
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

    methods: {
      openDoc: function () {
        this.$emit('event-open-doc', this.doc.pid);
      },

      toggleSelection: function () {
        if (this.$store.getters.FTLDocumentSelected(this.doc.pid)) {
          this.$store.commit("unselectDocument", this.doc)
        } else {
          this.$store.commit("selectDocuments", [this.doc])
        }
      },

      stop_spinner: function () {
        this.timeout_spinner = true;
      }
    }
  }
</script>

<style scoped lang="scss">
  .document-title {
    color: map_get($theme-colors, 'primary');
    line-height: calc(1.3rem + (0.25rem * 2) + (1px * 2));
  }

  .card {
    border-color: rgba(0, 0, 0, 0.250);
    border-radius: calc(0.25rem - 1px);

    &:hover {
      border-color: map_get($theme-colors, 'primary');
    }
  }

  .selected {
    border-color: transparent;
    box-shadow: 0 0 0 2px map_get($theme-colors, 'active');

    &:hover {
      border-color: transparent;
      box-shadow: 0 0 0 2px map_get($theme-colors, 'primary');
    }
  }

  .card-img-top {
    height: 200px;
    box-shadow: inset 0 -10px 30px -30px #0A0A0A;
    background-repeat: no-repeat;
    background-size: cover;
    transition: background-position 1.2s cubic-bezier(.68, -0.55, .27, 1.55) 1s,
    box-shadow 1.2s ease-in-out 1s;
    cursor: pointer;
    border-bottom: 1px solid rgba(0, 0, 0, 0.125);
  }

  .card-title {
    cursor: pointer;
    font-size: 1.1rem;
    margin-bottom: 0;
  }

  .card-img-top:hover {
    background-position: bottom;
    box-shadow: inset 0 10px 30px -30px #0A0A0A;
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
</style>
