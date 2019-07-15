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
        <b-button class="m-1" variant="secondary" size="sm" :href="'uploads/' + doc.pid">
          <font-awesome-icon icon="file-download" :alt="this.$_('Download')"/>
        </b-button>
        <b-button class="delete-document m-1" variant="danger" size="sm" :disabled="deleting"
                  @click="deleteDocument">
          <b-spinner :class="{'d-none': !deleting}" small></b-spinner>
          <span :class="{'d-none': deleting}"><font-awesome-icon icon="trash" :alt="this.$_('Delete')"/></span>
        </b-button>
      </b-card-body>
      <b-card-footer>
        <small class="text-muted">{{ $moment(doc.created).fromNow() }}</small>
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

    methods: {
      openDoc: function () {
        this.$emit('event-open-doc', this.doc.pid);
      },

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
