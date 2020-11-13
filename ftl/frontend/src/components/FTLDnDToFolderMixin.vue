<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the Business Source License. See LICENSE at project root for more information.
  -->
<script>
import FTLMoveDocuments from "@/components/FTLMoveDocuments";

export default {
  name: "FTLDnDToFolderMixin",
  mixins: [FTLMoveDocuments], // Reuse methods for moving documents

  props: {
    folder: {
      type: Object,
      required: false,
      default: function () {
        return {};
      },
    },
    docs: {
      type: Array,
      required: false,
      default: function () {
        return [];
      },
    },
  },

  data() {
    return {
      dragOver: false,
    };
  },
  methods: {
    drop: function (event) {
      let pid = event.dataTransfer.getData("application/ftl-pid");

      if (pid) {
        this.docs.push({ pid: pid }); // Fake a doc
        this.$store.commit("selectMoveTargetFolder", {
          id: this.folder.id,
          name: this.folder.name,
        });
        this.moveDocument();
        this.docs.length = 0; // Clear docs array
      }

      this.dragOver = false;
    },

    allowDrop: function (event) {
      // element doesn't allow dropping by default, we need to prevent default to allow dropping.
      event.preventDefault();
      this.dragOver = true;
    },

    leaveDrop: function (event) {
      this.dragOver = false;
    },
  },
};
</script>
