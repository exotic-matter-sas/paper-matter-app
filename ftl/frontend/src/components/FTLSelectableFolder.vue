<template>
  <b-col
    sm="2"
    class="m-1 folder"
    :class="{selected: selected}"
    @dblclick="dbClickFolder"
    @click="clickFolder">
    <b-row align-h="center">
      <b-col>
        <font-awesome-icon icon="folder" size="5x" class="text-secondary"/>
      </b-col>
    </b-row>
    <b-row align-h="center">
      <b-col>{{ folder.name }}</b-col>
    </b-row>
  </b-col>
</template>

<script>

  export default {
    name: "FTLSelectableFolder",

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
      dbClickFolder: function () {
        this.$emit('event-navigate-folder', this.folder);
      },

      clickFolder: function () {
        this.selected = !this.selected;
        if (this.selected) {
          this.$emit('event-select-folder', this.folder);
          // Store the selected panel folder for usage by ManageFolders.vue for displaying the folder detail panel
          this.$store.commit('selectPanelFolder', this.folder);
        } else {
          this.$emit('event-unselect-folder');
          this.$store.commit('selectPanelFolder', null);
        }
      }
    }
  }
</script>

<style scoped lang="scss">
  @import '../styles/customBootstrap.scss';

  .folder {
    cursor: pointer;
    border: 3px solid transparent;
  }

  .selected {
    border: 3px solid $em-orange;
  }
</style>
