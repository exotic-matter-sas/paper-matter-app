<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <li class="folder-tree-item">
    <b-link class="expand-folder-child" v-if="item.has_descendant && !item.is_root" @click="toggle">
      <b-spinner v-if="loading" small></b-spinner>
      <font-awesome-icon v-else :icon="isOpen ? ['far', 'minus-square'] : ['far', 'plus-square']"/>
    </b-link>
    <b-link @click.prevent="selectFolder" @dblclick.prevent="toggle" :disabled="item.id === folderToDisable"
            class="d-block  "
            :class="{'font-weight-bold': item.has_descendant, selected: $store.getters.FTLTreeItemSelected(item.id)}">
      <span v-if="item.id === folderToDisable && folderToDisableMessage !== null"
            class="text-muted font-italic float-right font-weight-normal">
          {{ folderToDisableMessage }}
      </span>
      <span class="target-folder-name mx-2" :title="item.name">
        <font-awesome-icon :icon="isOpen || item.is_root ? 'folder-open' : 'folder'"/>
        {{ item.name }}
      </span>
    </b-link>
    <ul class="pl-4" v-show="isOpen || item.is_root" v-if="'children' in item && item.children.length > 0">
      <FTLTreeItem
        class="item"
        v-for="folder in item.children"
        :key="folder.id"
        :item="folder"
        :folder-to-disable="folderToDisable"
        :folder-to-disable-message="folderToDisableMessage"
        :folder-to-hide="folderToHide"
      ></FTLTreeItem>
    </ul>
    <ul class="pl-4" v-else-if="lastFolderListingFailed">
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
      // to disable a folder selection
      folderToDisable: {default: -1},
      // to display an informative message next to the disabled folder
      folderToDisableMessage: {type: String, default: null},
      // to hide a folder from the list (eg. when moving a folder it can't be move to itself or one of its child)
      folderToHide: {default: -1},
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
                  return e.id !== vi.folderToHide;
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

  .expand-folder-child{
    position: absolute;
    margin-left: -1rem;
  }

  .selected {
    background: map_get($theme-colors, 'active');
    color:white;

    &:hover{
      color:white;
    }
  }

  svg {
    vertical-align: -0.125em;
  }

  .target-folder-name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    display: block;
    color: map_get($theme-colors, 'dark-grey');
  }
</style>
