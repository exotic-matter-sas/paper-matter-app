<!--
  - Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <b-col sm="2" class="m-1 folder" :class="{ selected: state }">
    <b-row class="icon" align-h="center">
      <b-col @click="navigateToFolder">
        <font-awesome-icon
          icon="folder"
          size="5x"
          class="text-secondary w-100"
          :class="{ 'highlight-animation': folder.highlightAnimation }"
        />
      </b-col>
    </b-row>
    <b-row align-h="start" no-gutters>
      <b-col>
        <b-form-checkbox :id="'checkbox-folder-' + folder.id" v-model="state">
          <span :title="folder.name" class="text-wrap text-break">{{
            folder.name
          }}</span>
        </b-form-checkbox>
      </b-col>
    </b-row>
  </b-col>
</template>

<script>
import { mapState } from "vuex";

export default {
  name: "FTLSelectableFolder",

  props: {
    folder: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      state: false,
    };
  },

  computed: {
    ...mapState(["panelSelectedFolder"]), // generate vuex computed getter
  },

  watch: {
    panelSelectedFolder: function (newVal, oldVal) {
      // Watch the global selected folder panel and deselect itself if any other folder is selected
      if (
        this.panelSelectedFolder !== null &&
        this.panelSelectedFolder.id !== this.folder.id
      ) {
        this.state = false;
      }
    },
    state: function (newVal, oldVal) {
      if (newVal === true) {
        this.$emit("event-select-folder", this.folder);
        // Store the selected panel folder for usage by FTLManageFoldersPanel.vue for displaying the folder detail panel
        this.$store.commit("selectPanelFolder", this.folder);
      } else {
        this.$emit("event-unselect-folder", this.folder);
        this.$store.commit("selectPanelFolder", null);
      }
    },
  },

  methods: {
    navigateToFolder: function () {
      this.$emit("event-navigate-folder", this.folder);
    },
  },
};
</script>

<style scoped lang="scss">
.folder {
  border: 3px solid transparent;

  .icon {
    cursor: pointer;
  }
}

.folder.selected .icon svg {
  stroke: $em-orange;
  stroke-width: 0.25em;
}
</style>

<style scoped lang="scss">
@import "~bootstrap/scss/_functions.scss";
@import "~bootstrap/scss/_variables.scss";
@import "~bootstrap/scss/_mixins.scss";

.folder .custom-control {
  margin-left: -1.5rem;

  label {
    cursor: pointer;

    span {
      white-space: nowrap;
      text-overflow: ellipsis;
      display: block;
      overflow: hidden;
    }
  }
}

@include media-breakpoint-up(sm) {
  .folder .custom-control label {
    width: 100%;

    span {
      white-space: nowrap;
      text-overflow: ellipsis;
      width: 100%;
      display: block;
      overflow: hidden;
    }
  }
}

.highlight-animation path {
  animation: highlight 2s ease-in;
}
</style>
