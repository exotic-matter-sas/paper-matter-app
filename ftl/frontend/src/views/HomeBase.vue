<!--
  - Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <div></div>
</template>

<i18n>
  fr:
    Unable to load more document: Erreur lors du chargement de la suite des documents
    Unable to refresh documents list: Erreur lors du chargement de la liste des documents
</i18n>

<script>
import { mapState } from "vuex";
import axios from "axios";
import qs from "qs";

export default {
  name: "home-base",

  props: ["doc"],

  data() {
    return {
      docs: [],
      docPid: null,
      docsLoading: false,
      moreDocsLoading: false,
      moreDocs: null,
      sort: null,
      count: 0,
      currentRenameDoc: {},
      droppedFiles: [],
      draggingFilesToDocsList: false,
    };
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
        this.docPid = null;
      } else {
        if (newVal !== oldVal) {
          this.openDocument(newVal);
        }
      }
    },
  },

  computed: {
    ...mapState(["selectedDocumentsHome"]), // generate vuex computed getter
  },

  methods: {
    navigateToDocument: function (pid) {
      this.$router.push({ query: { doc: pid } });
    },

    openDocument: function (pid) {
      this.docPid = pid;
    },

    documentClosed: function (event) {
      // always force document update in list when document panel is closed (useful for doc renamed or just processed)
      this.documentUpdated(event);
      this.docPid = null;
      this.$router.push({ path: this.$route.path });
    },

    loadMoreDocuments: function () {
      const vi = this;
      this.moreDocsLoading = true;
      axios
        .get(this.moreDocs)
        .then((response) => {
          this.moreDocsLoading = false;
          vi.docs = vi.docs.concat(response.data["results"]);
          vi.count = response.data["count"];
          vi.moreDocs = response.data["next"];
        })
        .catch((error) => {
          this.moreDocsLoading = false;
          vi.mixinAlert(this.$t("Unable to load more document"), true);
        });
    },

    _updateDocuments: function (query) {
      let queryString = {};

      if (this.sort === "az") {
        queryString["ordering"] = "title";
      } else if (this.sort === "za") {
        queryString["ordering"] = "-title";
      } else if (this.sort === "older") {
        queryString["ordering"] = "created";
      } else if (this.sort === "recent") {
        queryString["ordering"] = "-created";
      }

      let strQueryString = "?" + qs.stringify({ ...query, ...queryString });

      this.docsLoading = true;

      axios
        .get("/app/api/v1/documents" + strQueryString)
        .then((response) => {
          this.docsLoading = false;
          this.docs = response.data["results"];
          this.count = response.data["count"];
          this.moreDocs = response.data["next"];
          // Reset last opened doc
          this.$store.commit("setLastOpenedDocument", null);
        })
        .catch((error) => {
          this.docsLoading = false;
          this.mixinAlert(this.$t("Unable to refresh documents list"), true);
        });
    },

    documentDeleted: function (event) {
      const doc = event.doc;
      const foundIndex = this.docs.findIndex((x) => x.pid === doc.pid);
      this.docs.splice(foundIndex, 1);
      this.count--;
      // remove from selection
      this.$store.commit("unselectDocument", doc);
      // if last doc in the list has been removed and there are more docs, refresh list
      if (this.docs.length < 1 && this.moreDocs !== null) {
        this.updateDocuments();
      }
    },

    documentUpdated: function (event) {
      const doc = event.doc;

      const foundIndex = this.docs.findIndex((x) => x.pid === doc.pid);
      this.$set(this.docs, foundIndex, doc); // update doc in the list (force reactivity)
    },

    showDropZone: function (event) {
      // only show drop zone when dragging a file
      if (event.dataTransfer.types.includes("Files")) {
        event.preventDefault();
        this.draggingFilesToDocsList = true;
      }
    },

    allowDrop: function (event) {
      // element doesn't allow dropping by default, we need to prevent default to allow dropping
      event.preventDefault();
    },

    getDroppedFiles: function (event) {
      event.preventDefault();
      this.droppedFiles = Array.from(event.dataTransfer.files);
      this.draggingFilesToDocsList = false;
    },

    hideDropZone: function (event) {
      this.draggingFilesToDocsList = false;
    },
  },
};
</script>
