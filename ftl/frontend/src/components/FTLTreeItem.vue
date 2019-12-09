<!--
  - Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <li class="folder-tree-item">
    <span
      :class="{bold: item.has_descendant, selected: $store.getters.FTLTreeItemSelected(item.id)}">
      <span class="target-folder-name" @click="selectFolder">{{ item.name }}&nbsp;</span>
      <span class="expand-folder-child" v-if="item.has_descendant && !loading" @click="toggle">[{{ isOpen ? '-' : '+' }}]</span>
      <b-spinner :class="{'d-none': !loading}" small></b-spinner>
    </span>

    <ul v-show="isOpen" v-if="item.has_descendant">
      <FTLTreeItem
        class="item"
        v-for="folder in item.children"
        :key="folder.id"
        :item="folder"
        :source-folder="sourceFolder">
      </FTLTreeItem>
    </ul>
  </li>
</template>

<script>
  import axios from 'axios';

  export default {
    name: "FTLTreeItem",

    props: {
      item: {
        type: Object,
        required: true
      },
      sourceFolder: {
        type: Number,
        required: true
      },
    },

    data() {
      return {
        loading: false,
        isOpen: false
      }
    },

    methods: {
      toggle: function () {
        this.isOpen = !this.isOpen;

        if (this.item.has_descendant && this.isOpen) {
          this.updateMovingFolder(this.item.id);
        }

        if (!this.isOpen) {
          this.item.children = [];
        }
      },

      selectFolder: function () {
        if (this.$store.getters.FTLTreeItemSelected(this.item.id)) {
          this.$store.commit('selectMoveTargetFolder', null);
        } else {
          this.$store.commit('selectMoveTargetFolder', {id: this.item.id, name: this.item.name})
        }
      },

      updateMovingFolder: function (level = null) {
        const vi = this;
        let qs = '';

        if (level) {
          qs = '?level=' + level;
        }

        this.loading = true;
        axios
          .get("/app/api/v1/folders" + qs)
          .then(response => {
              vi.item.children = response.data
                .filter(function (e) {
                  return e.id !== vi.sourceFolder;
                })
                .map(function (e) {
                  return {id: e.id, name: e.name, has_descendant: e.has_descendant, children: []}
                })
            }
          )
          .catch(error => vi.mixinAlert(vi.$_('Unable to refresh folders list'), true))
          .finally(() => this.loading = false);
      }
    }
  }
</script>


<style scoped lang="scss">
  @import '../styles/customBootstrap.scss';

  .bold {
    font-weight: bold;
  }

  .item {
    cursor: pointer;
  }

  .selected {
    background: map_get($theme-colors, 'active');
  }
</style>
