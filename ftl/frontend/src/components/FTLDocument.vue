<template>
  <b-col sm="3" :id="doc.pid" class="document-thumbnail">
    <b-row class="text-truncate document-title"><span
      @click="$emit('event-open-doc', doc.pid)">{{ doc.title }}</span></b-row>
    <b-row align-h="center">
      <b-img :src="'/app/api/v1/documents/' + doc.pid + '/thumbnail.png'" class="img-thumbnail" slot="aside"
             blank-color="#abc"
             @click="$emit('event-open-doc', doc.pid)"
             onerror="this.src='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJYAAADICAQAAACgjNDuAAABIElEQVR42u3QAQEAAAgCIP0/ui44ACbQXBhVlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVr9/mzyAFGRN6/AAAAAElFTkSuQmCC\n'"/>
    </b-row>
    <b-row>
      <small>{{ getDate }}</small>
    </b-row>
    <b-row align-h="center">{{this.$_('Note: ')}}{{ doc.note }}</b-row>

    <b-row>
      <b-col>
        <b-button variant="secondary" size="sm" :href="'uploads/' + doc.pid">{{this.$_('Download')}}</b-button>
      </b-col>
      <b-col>
        <b-button class="delete-document" variant="danger" size="sm" :disabled="deleting"
                  @click.once="deleteDocument">
          <b-spinner :class="{'d-none': !deleting}" small></b-spinner>
          <span :class="{'d-none': deleting}">{{this.$_('!! Delete doc (no warn) !!')}}</span>
        </b-button>
      </b-col>
    </b-row>
  </b-col>
</template>

<script>
  import axios from 'axios';
  import {axiosConfig} from "../constants";

  export default {
    props: {
      doc: {
        type: Object,
        required: true
      }
    },

    data() {
      return {
        deleting: false
      }
    },

    computed: {
      getDate: function () {
        return new Date(this.doc.created);
      }
    },

    methods: {
      deleteDocument: function () {
        let vi = this;
        vi.deleting = true;

        axios
          .delete('/app/api/v1/documents/' + this.doc.pid, axiosConfig)
          .then(() => vi.$emit('event-delete-doc'))
          .catch(error => vi.mixinAlert('Could not delete document', true));
      }
    }
  }
</script>

<style scoped>
  .img-thumbnail {
    max-height: 200px;
  }
</style>
