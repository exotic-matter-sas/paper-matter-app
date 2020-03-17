<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <li class="folder-tree-item">
    <span @click.prevent="selectFolder" @dblclick.prevent="toggle"
          class="px-1"
          :class="{'font-weight-bold': item.has_descendant, selected: $store.getters.FTLTreeItemSelected(item.id)}">
      <span class="target-folder-name">
        <font-awesome-icon :icon="isOpen || item.is_root ? 'folder-open' : 'folder'"/>
        &nbsp;{{ item.name }}&nbsp;
      </span>
      <b-spinner :class="{'d-none': !loading}" small></b-spinner>
    </span>
    <span class="expand-folder-child" v-if="item.has_descendant && !loading && !item.is_root" @click="toggle">
      [{{ isOpen ? '-' : '+' }}]
    </span>
    <ul class="pl-3" v-show="isOpen || item.is_root" v-if="children in item && item.children.length > 0">
      <FTLTreeItem
        class="item"
        v-for="folder in item.children"
        :key="folder.id"
        :item="folder"
        :source-folder="sourceFolder"
      ></FTLTreeItem>
    </ul>
    <ul class="pl-3" v-else-if="lastFolderListingFailed">
      <li class="text-danger">
        {{ $t('Folders can\'t be loaded') }}
      </li>
    </ul>
  </li>
</template>

<i18n>
  fr:
    Folders can't be loaded: Les dossiers n'ont pu être chargés
</i18n>

<script>
  import axios from 'axios';

  export default {
    name: "FTLTreeItem",

    props: {
      item: {
        type: Object,
        required: true
      },
       // to hide source folder in folder list
      sourceFolder: {
        type: Number,
        required: true
      },
    },

    data() {
      return {
        loading: false,
        isOpen: false,
        lastFolderListingFailed: false,
      }
    },

    methods: {
      toggle: function () {
        if (this.item.has_descendant && !this.loading && !this.item.is_root){
          this.isOpen = !this.isOpen;
          this.lastFolderListingFailed = false;

          if (this.item.has_descendant && this.isOpen) {
            this.listItemChildren(this.item.id);
          }

          if (!this.isOpen) {
            this.item.children = [];
          }
        }
      },

      selectFolder: function () {
        if (this.$store.getters.FTLTreeItemSelected(this.item.id)) {
          this.$store.commit('selectMoveTargetFolder', null);
        } else {
          this.$store.commit('selectMoveTargetFolder', {id: this.item.id, name: this.item.name})
        }
      },

      listItemChildren: function (level = null) {
        const vi = this;
        let qs = '';
        vi.lastFolderListingFailed = false;

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
          .catch(error => vi.lastFolderListingFailed = true )
          .finally(() => this.loading = false);
      }
    }
  }
</script>


<style scoped lang="scss">
  ul{
    list-style: none;
    user-select: none;
  }

  .item {
    cursor: pointer;
  }

  .selected {
    background: map_get($theme-colors, 'active');
  }

  svg {
    vertical-align: -0.125em;
  }
</style>
