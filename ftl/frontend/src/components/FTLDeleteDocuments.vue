<template>
  <b-modal id="modal-delete-documents"
           :title="$_('Delete documents')"
           ok-variant="danger"
           :ok-title="$_('Delete')"
           :cancel-title="$_('Cancel')"
           @ok="deleteDocuments">
    {{ $_('Please confirm that you want to delete %s documents', [docs.length]) }}
  </b-modal>
</template>
<script>

  import axios from "axios";
  import {axiosConfig} from "@/constants";

  export default {
    name: 'FTLDeleteDocuments',

    props: {
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
