<!--
  - Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <b-button class="folder" :disabled="navigating" @click="navigate">
    <b-spinner id ="folder-list-loader" :class="{'d-none': !navigating}" small></b-spinner>
    <span :class="{'d-none': navigating}">{{ folder.name }}</span>
  </b-button>
</template>

<script>
  export default {
    name: "FTLFolder",

    props: {
      folder: {
        type: Object,
        required: true
      },


    },

    data() {
      return {
        navigating: false
      }
    },

    methods: {
      navigate: function () {
        this.navigating = true;
        this.$emit('event-change-folder', this.folder);
      }
    }
  }
</script>

<style scoped>

</style>
