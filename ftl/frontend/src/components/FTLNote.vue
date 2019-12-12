<!--
  - Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <b-row>
    <b-col id="note-title" cols="12" class="mb-1">
      <h6 class="d-inline font-weight-bold">{{ $_('Note') }}</h6>
      <b-button v-if="!editing" id="edit-note" variant="link" size="sm" @click.prevent="editing = true">
        <font-awesome-icon icon="edit" :title="$_('Edit note')"/>
      </b-button>
    </b-col>

    <b-col v-if="editing" id='note-form'>
      <b-row>
        <b-col>
          <b-tabs content-class="mt-2" small lazy>
            <b-tab :title="$_('Edition')" active>
              <b-form-textarea
                id="note-textarea"
                v-model="text"
                :placeholder="$_('Document note ...')"
                max-rows="10">
              </b-form-textarea>
            </b-tab>
            <b-tab :title="$_('Preview')">
              <div id="note-preview"><span v-html="getNoteMarkdownSanitized"></span></div>
            </b-tab>
          </b-tabs>
        </b-col>
      </b-row>
      <b-row id="note-toolbar" class="mt-2" align-v="center">
        <b-col>
          <div id="note-tip">
            <a v-if="doc.note === text" class="text-muted" :title="$_('Markdown syntax supported')"
               href="https://guides.github.com/features/mastering-markdown/#examples" target="_blank">
              <font-awesome-icon :icon="['fab', 'markdown']" rel="Markdown logo"/>
              {{ $_(' supported') }}
            </a>
            <span v-else class="highlight">
              <font-awesome-icon icon="exclamation-circle"/>
              {{$_('unsaved note')}}
            </span>
          </div>
        </b-col>
        <b-col class="text-right">
          <b-button variant="link" size="sm" :disabled="editing === false"
                    @click.prevent="cancelUpdate">
            {{$_('Cancel')}}
          </b-button>
          <b-button id="save-note" variant="primary" size="sm" :disabled="doc.note === text"
                    @click.prevent="updateNote">
            {{$_('Save')}}
          </b-button>
        </b-col>
      </b-row>
    </b-col>

    <b-col v-else-if="doc.note">
      <div id="note"><span v-html="getNoteMarkdownSanitized"></span></div>
    </b-col>

    <b-col v-else>
      <span class="text-muted font-italic">{{$_('No note set')}}</span>
    </b-col>
  </b-row>
</template>

<script>
  import marked from "marked";
  import dompurify from "dompurify";
  import axios from "axios";
  import {axiosConfig, markedConfig} from "@/constants";

  export default {
    name: 'FTLNote',

    props: {
      doc: {
        type: Object,
        required: true
      }
    },

    data() {
      return {
        editing: false,
        text: this.doc.note
      }
    },

    computed: {
      getNoteMarkdownSanitized: function () {
        const markdownHtml = marked(this.text, markedConfig);
        return dompurify.sanitize(markdownHtml);
      }
    },

    methods: {
      updateNote: function () {
        this.editing = false;

        let body = {
          note: this.text
        };

        axios
          .patch('/app/api/v1/documents/' + this.doc.pid, body, axiosConfig)
          .then(response => {
            this.$emit('event-document-note-edited', {doc: response.data});
            this.mixinAlert('Document note saved!');
          })
          .catch(error => {
            this.mixinAlert(this.$_('Could not save note'), true)
          });
      },

      cancelUpdate: function () {
        this.editing = false;
        this.text = this.doc.note;
      }
    }
  }
</script>

<style scoped lang="scss">
  @import '../styles/customBootstrap.scss';

  #note-title { // to avoid #note-form visible behind title during animation
    background: white;
    z-index: $zindex-dropdown;

    .btn { // to avoid wobbly UI when button disappear
      padding-top: 0;
      padding-bottom: 0;
    }
  }

  #note {
    overflow: auto;
    max-height: 50vh;
  }

  #note-tip {
    font-size: 0.9rem;
  }

  #note-form {
    animation: slide-down 0.2s linear;
  }
</style>

