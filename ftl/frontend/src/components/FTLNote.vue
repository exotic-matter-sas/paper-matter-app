<template>
  <b-row class="my-1">
    <b-col v-if="editing || doc.note">
      <b-row v-if="editing">
        <b-col>
          <b-row>
            <b-col>
              <b-tabs content-class="mt-3" small lazy>
                <b-tab :title="$_('Note')" active>
                  <b-form-textarea
                    id="edit-note"
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
          <b-row class="my-1" align-v="center">
            <b-col>
              <b-button class="m-1" variant="link" size="sm" :disabled="editing === false"
                        @click.prevent="editing = false">
                {{$_('Close')}}
              </b-button>
              <b-button class="m-1" variant="primary" size="sm" :disabled="doc.note === text"
                        @click.prevent="updateNote">
                {{$_('Save')}}
              </b-button>
              <span class="font-weight-bold" :class="{'d-none': doc.note === text}">{{$_('Unsaved note!')}}</span>
            </b-col>
          </b-row>
        </b-col>
      </b-row>

      <b-row v-else>
        <b-col>
          <div class="note" @click.prevent="editing = true"><span v-html="getNoteMarkdownSanitized"></span></div>
        </b-col>
      </b-row>
    </b-col>
    <b-col v-else>
      <b-button variant="primary" @click.prevent="editing = true">{{ $_('Add a note...') }}</b-button>
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
        const markdownHtml = marked(this.text, {gfm: true});
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
</style>

