<template>
  <b-col
    sm="2"
    class="m-1 folder"
    :class="{selected: selected}"
    @dblclick="$emit('event-navigate-folder', folder.id)"
    @click="clickFolder">
    <b-row align-h="center">
      <font-awesome-icon icon="folder" size="5x"/>
    </b-row>
    <b-row align-h="center">
      <b>{{ folder.name }}</b>
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
    },

    data() {
      return {
        selected: false
      }
    },

    computed: {
      globalSelected: function () {
        // allow to watch the value
        return this.$store.state.panelSelectedFolder;
      }
    },

    watch: {
      globalSelected: function (newVal, oldVal) {
        // Watch the global selected folder panel and deselect itself if any other folder is selected
        if (this.globalSelected !== null && this.globalSelected.id !== this.folder.id) {
          this.selected = false;
        }
      }
    },

    methods: {
      clickFolder: function () {
        this.selected = !this.selected;
        if (this.selected) {
          this.$emit('event-select-folder', this.folder.id);
          // Store the selected panel folder for usage by Folders.vue for displaying the folder detail panel
          this.$store.commit('selectPanelFolder', this.folder);
        } else {
          this.$emit('event-unselect-folder');
          this.$store.commit('selectPanelFolder', null);
        }
      }
    }
  }
</script>

<style scoped>
  .folder {
    cursor: pointer;
  }

  .selected {
    border: 3px solid dodgerblue;
  }
</style>
