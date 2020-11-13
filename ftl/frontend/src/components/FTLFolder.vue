<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the Business Source License. See LICENSE at project root for more information.
  -->

<template>
  <b-button
    class="folder"
    :class="{
      'border border-active': dragOver,
      'highlight-animation': folder.highlightAnimation,
    }"
    :disabled="navigating"
    @click="navigate"
    @drop="drop"
    @dragover="allowDrop"
    @dragleave="leaveDrop"
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
import FTLDnDToFolderMixin from "@/components/FTLDnDToFolderMixin";

export default {
  name: "FTLFolder",
  mixins: [FTLDnDToFolderMixin], // Reuse methods for moving documents

  data() {
    return {
      navigating: false,
    };
  },

  methods: {
    navigate: function () {
      this.navigating = true;
      this.$emit("event-change-folder", this.folder);
    },
  },
};
</script>

<style scoped>
.highlight-animation {
  animation: highlight 2s ease-in;
}
</style>
