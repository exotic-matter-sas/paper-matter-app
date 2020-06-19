<!--
  - Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <b-button
    class="folder"
    :class="{ 'border border-primary': dragOver }"
    :disabled="navigating"
    @click="navigate"
    v-on:drop="drop"
    v-on:dragover="allowDrop"
    v-on:dragleave="leaveDrop"
  >
    <b-spinner
      id="folder-list-loader"
      :class="{ 'd-none': !navigating }"
      small
    ></b-spinner>
    <span :class="{ 'd-none': navigating }">{{ folder.name }}</span>
  </b-button>
</template>

<script>
import FTLMoveDocuments from "@/components/FTLMoveDocuments";

export default {
  name: "FTLFolder",
  mixins: [FTLMoveDocuments], // Reuse methods for moving documents

  props: {
    folder: {
      type: Object,
      required: true,
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
      navigating: false,
      dragOver: false,
    };
  },

  methods: {
    navigate: function () {
      this.navigating = true;
      this.$emit("event-change-folder", this.folder);
    },

    drop: function (event) {
      let pid = event.dataTransfer.getData("pid");

      if (pid) {
        this.docs.push({ pid: pid }); // Fake a doc
        this.$store.commit("selectMoveTargetFolder", {
          id: this.folder.id,
          name: this.folder.name,
        });
        this.moveDocument();
        this.docs.length = 0; // Clear docs array
      }
    },

    allowDrop: function (evt) {
      // prevent default to allow drop (weird)
      evt.preventDefault();
      this.dragOver = true;
    },

    leaveDrop: function (evt) {
      this.dragOver = false;
    },
  },
};
</script>

<style scoped></style>
