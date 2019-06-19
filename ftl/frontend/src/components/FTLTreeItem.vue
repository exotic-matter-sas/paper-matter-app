<template>
  <li>
    <span
      :class="{bold: isFolder, selected: selected}">
      <span @click="selectFolder">{{ item.name }}&nbsp;</span>
      <span v-if="isFolder && !loading" @click="toggle">[{{ isOpen ? '-' : '+' }}]</span>
      <b-spinner :class="{'d-none': !loading}" small></b-spinner>
    </span>

    <ul v-show="isOpen" v-if="isFolder">
      <FTLTreeItem
        class="item"
        v-for="folder in item.children"
        :key="folder.id"
        :item="folder">
      </FTLTreeItem>
    </ul>
  </li>
</template>

<script>
  import axios from 'axios';

  export default {
    name: "FTLTreeItem",

    props: {
      item: Object
    },

    data: function () {
      return {
        loading: false,
        isOpen: false
      }
    },

    computed: {
      isFolder: function () {
        return this.item.has_descendant
      },

      selected: function () {
        return !!(this.$store.state.selectedMoveTargetFolder
          && this.$store.state.selectedMoveTargetFolder.id === this.item.id);
      }
    },

    methods: {
      toggle: function () {
        this.isOpen = !this.isOpen;

        if (this.isFolder && this.isOpen) {
          this.updateMovingFolder(this.item.id);
        }
      },

      selectFolder: function () {
        if (this.selected) {
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
          .get("/app/api/v1/folders/" + qs)
          .then(response => {
              vi.item.children = response.data.map(function (e) {
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


<style scoped>
  .bold {
    font-weight: bold;
  }

  .item {
    cursor: pointer;
  }

  .selected {
    background: dodgerblue;
  }
</style>
