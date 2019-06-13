<template>
  <b-button class="folder m-1" :disabled="navigating" @click="navigate">
    <b-spinner :class="{'d-none': !navigating}" small></b-spinner>
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
