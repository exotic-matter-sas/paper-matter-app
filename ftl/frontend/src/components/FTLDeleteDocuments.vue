<template>
  <b-modal :id="id"
           :title="$_('Delete documents')"
           ok-variant="danger"
           :ok-title="$_('Delete')"
           :cancel-title="$_('Cancel')"
           @ok="deleteDocuments">
    <span v-if="docs.length > 1">{{ $_('Please confirm that you want to delete %s documents', [docs.length]) }}</span>
    <span v-else>{{ $_('Please confirm that you want to delete %s', [docs[0].title])}}</span>
  </b-modal>
</template>
<script>

  import axios from "axios";
  import {axiosConfig} from "@/constants";

  export default {
    name: 'FTLDeleteDocuments',

    props: {
      // customize the id to allow multiple time this component in Home
      // Used one time for batch delete document
      // TODO next, in doc panel?
      id: {
        type: String,
        default: "modal-delete-documents"
      },
      docs: {
        type: Array,
        required: true
      }
    },

    data() {
      return {}
    },

    methods: {
      deleteDocuments: function () {
        for (const doc of this.docs) {
          axios
            .delete('/app/api/v1/documents/' + doc.pid, axiosConfig)
            .then((response) => {
              this.$emit('event-document-deleted', {'doc': doc})
            })
            .catch(error => this.mixinAlert(this.$_('Could not delete document'), true));
        }
      }
    }
  }
</script>

<style>

</style>
