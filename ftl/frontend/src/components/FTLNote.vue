<template>
  <b-row>
    <b-col cols="12" class="mb-1">
      <h6 class="d-inline font-weight-bold">{{ $_('Note') }}</h6>
      <b-button v-if="!editing" id="edit-note" variant="link" size="sm">
        <font-awesome-icon icon="edit" :title="$_('Edit note')" @click.prevent="editing = true"/>
      </b-button>
    </b-col>

    <b-col v-if="editing">
      <b-row>
        <b-col>
          <b-tabs content-class="mt-2" small lazy>
            <b-tab :title="$_('Edition')" active>
              <b-form-textarea
                v-model="text"
                :placeholder="$_('Document note ...')"
                class="note"
                max-rows="10">
              </b-form-textarea>
            </b-tab>
            <b-tab :title="$_('Preview')">
              <div class="note"><span v-html="getNoteMarkdownSanitized"></span></div>
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
              {{ $_(' syntax supported') }}
            </a>
            <span v-else class="highlight">
              <font-awesome-icon icon="exclamation-circle"/>
              {{$_('unsaved note')}}
            </span>
          </div>
        </b-col>
        <b-col class="text-right">
          <b-button variant="link" size="sm" :disabled="editing === false"
                    @click.prevent="editing = false">
            {{$_('Cancel')}}
          </b-button>
          <b-button variant="primary" size="sm" :disabled="doc.note === text"
                    @click.prevent="updateNote">
            {{$_('Save')}}
          </b-button>
        </b-col>
      </b-row>
    </b-col>

    <b-col v-else-if="doc.note">
      <div class="note"><span v-html="getNoteMarkdownSanitized"></span></div>
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
  import {axiosConfig} from "@/constants";

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
        const markdownHtml = marked(this.text, {gfm: true, breaks: true});
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
            this.mixinAlert(this.$_('Could not save note!'), true)
          });
      }
    }
  }
</script>

<style scoped>
  .note {
    overflow: auto;
    max-height: 50vh;
  }

  #note-tip{
    font-size: 0.9rem;
  }
</style>

