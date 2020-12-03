<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the Business Source License. See LICENSE at project root for more information.
  -->

<template>
  <b-breadcrumb-item
    :to="to"
    :active="active"
    :class="{ 'drag-over': dragOver }"
    v-on:drop="drop"
    v-on:dragover="customAllowDrop"
    v-on:dragleave="leaveDrop"
  >
    <font-awesome-icon v-if="id === null" icon="home" />
    {{ text }}
  </b-breadcrumb-item>
</template>

<script>
import FTLDnDToFolderMixin from "@/components/FTLDnDToFolderMixin";

export default {
  name: "FTLBreadcrumbFolder",
  mixins: [FTLDnDToFolderMixin], // Reuse methods for moving documents

  props: ["id", "text", "to", "active"],

  methods: {
    customAllowDrop: function (event) {
      if (!this.active) this.allowDrop(event);
    },
  },
};
</script>

<style scoped lang="scss">
.breadcrumb-item a,
span {
  border: 1px solid transparent;
}

.drag-over a {
  border-color: map_get($theme-colors, "active");
}
</style>
