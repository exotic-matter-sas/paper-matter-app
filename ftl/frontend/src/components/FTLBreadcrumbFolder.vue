<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <b-breadcrumb-item
    :text="text"
    :to="to"
    :active="active"
    :class="{ 'border border-primary': dragOver }"
    v-on:drop="drop"
    v-on:dragover="customAllowDrop"
    v-on:dragleave="leaveDrop"
  />
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
