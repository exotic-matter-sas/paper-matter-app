<template>
  <b-col class="col-12 mb-4 col-sm-6 col-md-4 col-lg-3 col-xl-2 document-thumbnail" :id="doc.pid">
    <div class="card">
      <div class="card-img-top" slot="aside"
           :style="{'background-image': 'url(' + '/app/api/v1/documents/' + doc.pid + '/thumbnail.png' + ')'}"
           @click="$emit('event-open-doc', doc.pid)"></div>
      <b-card-body>
        <b-card-title class="text-truncate document-title" @click="$emit('event-open-doc', doc.pid)">
          {{ doc.title }}
        </b-card-title>
        <b-button variant="secondary" size="sm" :href="'uploads/' + doc.pid">{{this.$_('Download')}}</b-button>
        <b-button class="delete-document" variant="danger" size="sm" :disabled="deleting"
                  @click.once="deleteDocument">
          <b-spinner :class="{'d-none': !deleting}" small></b-spinner>
          <span :class="{'d-none': deleting}">{{this.$_('!! Delete doc (no warn) !!')}}</span>
        </b-button>
      </b-card-body>
      <b-card-footer>
        <small class="text-muted">{{ getDate }}</small>
      </b-card-footer>
    </div>
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
  .card-img-top {
    height: 200px;
    box-shadow: inset 0 -10px 30px -30px #0A0A0A;
    background-repeat: no-repeat;
    background-size: cover;
    transition: background-position 1.2s cubic-bezier(.68,-0.55,.27,1.55) 1s,
                box-shadow 1.2s ease-in-out 1s;
    cursor:pointer;
    border-bottom: 1px solid rgba(0, 0, 0, 0.125);
  }

  .card-title{
    cursor: pointer;
  }

  .card-img-top:hover {
    background-position: bottom;
    box-shadow: inset 0 10px 30px -30px #0A0A0A;
  }
</style>
