<script>
  import {mapState} from 'vuex'
  import FTLDocument from '@/components/FTLDocument';
  import FTLUpload from '@/components/FTLUpload';
  import FTLDeleteDocuments from "@/components/FTLDeleteDocuments";
  import FTLThumbnailGenMixin from "@/components/FTLThumbnailGenMixin";
  import FTLMoveDocuments from "@/components/FTLMoveDocuments";
  import FTLRenameDocument from "@/components/FTLRenameDocument";
  import axios from 'axios';
  import qs from 'qs';

  export default {
    name: 'home-base',
    mixins: [FTLThumbnailGenMixin],

    components: {
      FTLDeleteDocuments,
      FTLMoveDocuments,
      FTLRenameDocument,
      FTLDocument,
      FTLUpload
    },

    props: ['doc'],

    data() {
      return {
        // Documents list
        docs: [],
        docPid: null,
        docModal: false,
        lastRefresh: Date.now(),
        docsLoading: false,
        moreDocsLoading: false,
        moreDocs: null,
        sort: null,

        // PDF viewer
        currentOpenDoc: {},
        publicPath: process.env.BASE_URL
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
      sort: function (newVal, oldVal) {
        if (newVal !== oldVal) {
          this.updateDocuments()
        }
      }
    },

    computed: {
      ...mapState(['selectedDocumentsHome']) // generate vuex computed getter
    },

    methods: {
      refreshAll: function () {
        this.updateDocuments();
      },

      navigateToDocument: function (pid) {
        this.$router.push({query: {doc: pid}});
      },

      openDocument: function (pid) {
        const vi = this;

        this.docPid = pid;
        this.docModal = true;

        this.$bvModal.show('document-viewer');

        axios
          .get('/app/api/v1/documents/' + pid)
          .then(response => {
            vi.currentOpenDoc = response.data;

            if (!response.data.thumbnail_available) {
              vi.createThumbnailForDocument(response.data)
                .then(response => {
                  vi.mixinAlert("Thumbnail updated!");
                })
                .catch(error => vi.mixinAlert("Unable to create thumbnail", true));
            }
          })
          .catch(error => {
            vi.mixinAlert("Unable to show document.", true)
          });
      },

      closeDocument: function () {
        this.docModal = false;
        this.docPid = null;
        this.currentOpenDoc = {};
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
            vi.lastRefresh = Date.now();
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

        let strQueryString = '?' + qs.stringify({query, ...qs});

        this.docsLoading = true;

        axios
          .get('/app/api/v1/documents' + strQueryString)
          .then(response => {
            this.docsLoading = false;
            this.docs = response.data['results'];
            this.moreDocs = response.data['next'];
            this.lastRefresh = Date.now();
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

        if (this.currentOpenDoc.pid === doc.pid) {
          this.currentOpenDoc = doc; // update open doc
        }

        const foundIndex = this.docs.findIndex(x => x.pid === doc.pid);
        this.docs[foundIndex] = doc; // update doc in the list
      }
    }
  }
</script>
