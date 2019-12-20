<!--
  - Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <div></div>
</template>
<script>
  import {mapState} from 'vuex'
  import axios from 'axios';
  import qs from 'qs';

  export default {
    name: 'home-base',

    props: ['doc'],

    data() {
      return {
        // Documents list
        docs: [],
        docPid: null,
        docsLoading: false,
        moreDocsLoading: false,
        moreDocs: null,
        sort: null,
      }
    },

    mounted() {
      if (this.doc) {
        // Open document directly from loading an URL with document
        this.openDocument(this.doc);
      }
    },

    watch: {
      doc: function (newVal, oldVal) {
        if (newVal === undefined) {
          this.docModal = false;
        } else {
          if (newVal !== oldVal) {
            this.openDocument(newVal);
          }
        }
      },
    },

    computed: {
      ...mapState(['selectedDocumentsHome']) // generate vuex computed getter
    },

    methods: {
      navigateToDocument: function (pid) {
        this.$router.push({query: {doc: pid}});
      },

      openDocument: function (pid) {
        this.docPid = pid;
      },

      closeDocument: function () {
        this.docPid = null;
        this.$router.push({path: this.$route.path});
      },

      loadMoreDocuments: function () {
        const vi = this;
        this.moreDocsLoading = true;
        axios
          .get(this.moreDocs)
          .then(response => {
            this.moreDocsLoading = false;
            vi.docs = vi.docs.concat(response.data['results']);
            vi.moreDocs = response.data['next'];
          }).catch(error => {
          this.moreDocsLoading = false;
          vi.mixinAlert("Unable to load more document.", true);
        });
      },

      _updateDocuments: function (query) {
        let queryString = {};

        if (this.sort === 'az') {
          queryString['ordering'] = 'title';
        } else if (this.sort === 'za') {
          queryString['ordering'] = '-title';
        } else if (this.sort === 'older') {
          queryString['ordering'] = 'created';
        } else if (this.sort === 'recent') {
          queryString['ordering'] = '-created';
        }

        let strQueryString = '?' + qs.stringify({...query, ...queryString});

        this.docsLoading = true;

        axios
          .get('/app/api/v1/documents' + strQueryString)
          .then(response => {
            this.docsLoading = false;
            this.docs = response.data['results'];
            this.moreDocs = response.data['next'];
          }).catch(error => {
          this.docsLoading = false;
          this.mixinAlert("Unable to refresh documents list.", true);
        });
      },

      documentsCreated: function (event) {
        const doc = event.doc;
        this.docs.unshift(doc);
      },

      documentDeleted: function (event) {
        const doc = event.doc;
        const foundIndex = this.docs.findIndex(x => x.pid === doc.pid);
        this.docs.splice(foundIndex, 1);
        // remove from selection
        this.$store.commit('unselectDocument', doc);
        // if last doc in the list has been removed and there is more docs to come, refresh list
        if (this.docs.length < 1 && this.moreDocs !== null) {
          this.updateDocuments()
        }
      },

      documentUpdated: function (event) {
        const doc = event.doc;

        const foundIndex = this.docs.findIndex(x => x.pid === doc.pid);
        this.docs[foundIndex] = doc; // update doc in the list
      }
    }
  }
</script>
