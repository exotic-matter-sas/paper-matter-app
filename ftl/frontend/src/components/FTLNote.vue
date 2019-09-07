<template>
  <b-row>
    <b-col>
      <b-row class="my-1">
        <b-col>
          <b-form-textarea
            id="edit-note"
            v-model="text"
            :placeholder="$_('Document note ...')"
            rows="3"
            max-rows="8">
          </b-form-textarea>
        </b-col>
      </b-row>
      <b-row class="my-1">
        <b-col>
          <b-button class="m-1" variant="primary" size="sm" :disabled="doc.note === text" @click.prevent="updateNote">
            {{$_('Save')}}
          </b-button>
          <span class="font-weight-bold" :class="{'d-none': doc.note === text}">{{$_('Unsaved note!')}}</span>
        </b-col>
      </b-row>
    </b-col>
  </b-row>
</template>

<script>
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
        text: this.doc.note
      }
    },

    methods: {
      updateNote: function () {
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

<style scoped></style>

