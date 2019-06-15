<template>
  <b-col sm="2" class="m-1">
    <b-row align-h="center">
      <span @click="$emit('event-navigate-folder', folder)"><b>{{ folder.name }}</b></span>
    </b-row>
    <b-row align-h="center">
      {{ folder.created }}
    </b-row>
    <b-row align-h="center">
      <b-button class="m-1" variant="secondary" @click="$emit('event-move-folder', folder)">Move</b-button>
      <b-button class="m-1" variant="danger" @click="$emit('event-delete-folder', folder)">Delete</b-button>
    </b-row>
  </b-col>
</template>

<script>
  export default {
    name: "FTLOrganizeFolder",

    props: {
      folder: {
        type: Object,
        required: true
      }
    }
  }
</script>

<style scoped>

</style>
