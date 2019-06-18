<template>
  <b-col sm="3" :id="doc.pid" class="document-thumbnail">
    <b-row align-h="center" class="text-truncate document-title">
      <span @click="$emit('event-open-doc', doc.pid)">{{ doc.title }}</span>
    </b-row>
    <b-row align-h="center">
      <b-img thumbnail fluid
             :src="'/app/api/v1/documents/' + doc.pid + '/thumbnail.png'"
             class="img-thumbnail"
             slot="aside"
             blank-color="#abc"
             @click="$emit('event-open-doc', doc.pid)"
             onerror="this.src='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJYAAADICAQAAACgjNDuAAABIElEQVR42u3QAQEAAAgCIP0/ui44ACbQXBhVlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVLlixZsmTJkiVr9/mzyAFGRN6/AAAAAElFTkSuQmCC\n'"/>
    </b-row>
    <b-row align-h="center">
      <span :title="doc.created">{{ $moment(doc.created).fromNow() }}</span>
    </b-row>
    <!--    <b-row align-h="center">{{this.$_('Note: ')}}{{ doc.note }}</b-row>-->

    <b-row align-h="center">
      <b-col>
        <b-button class="m-1" variant="secondary" size="sm" :href="'uploads/' + doc.pid">
          <font-awesome-icon icon="file-download" :alt="this.$_('Download')"/>
        </b-button>
        <b-button class="delete-document m-1" variant="danger" size="sm" :disabled="deleting"
                  @click="deleteDocument">
          <b-spinner :class="{'d-none': !deleting}" small></b-spinner>
          <span :class="{'d-none': deleting}"><font-awesome-icon icon="trash" :alt="this.$_('Delete')"/></span>
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

    methods: {
      deleteDocument: function () {
        let vi = this;

        this.deleting = true;
        this.$bvModal.msgBoxConfirm(this.$_('Please confirm that you want to delete the document'), {
          title: this.$_('Deletion of the document'),
          size: 'md',
          buttonSize: 'md',
          okVariant: 'danger',
          okTitle: this.$_('Yes, I want to delete the document'),
          cancelTitle: this.$_('No, cancel'),
          footerClass: 'm-1',
          hideHeaderClose: false,
          centered: true
        })
          .then(value => {
            if (value === true) {
              axios
                .delete('/app/api/v1/documents/' + vi.doc.pid, axiosConfig)
                .then(() => vi.$emit('event-delete-doc'))
                .catch(error => vi.mixinAlert(this.$_('Could not delete document'), true));
            } else {
              vi.deleting = false;
            }
          });
      }
    }
  }
</script>

<style scoped>
  /*.img-thumbnail {*/
  /*  max-height: 200px;*/
  /*}*/
</style>
