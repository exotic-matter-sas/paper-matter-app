<template>
  <ul id="moving-folders">
    <FTLTreeItem
      class="item"
      v-for="folder in folders"
      :key="folder.id"
      :item="folder">
    </FTLTreeItem>
  </ul>
</template>

<script>
  import FTLTreeItem from "@/components/FTLTreeItem";
  import axios from 'axios';

  export default {
    name: 'FTLTreeFolders',
    components: {
      FTLTreeItem
    },
    props: ['start'],

    data() {
      return {
        folders: []
      }
    },

    mounted() {
      const vi = this;
      let qs = '';

      if (this.start) {
        qs = '?level=' + start;
      }

      axios
        .get("/app/api/v1/folders/" + qs)
        .then(response => {
            vi.folders = response.data.map(function (e) {
              return {id: e.id, name: e.name, has_descendant: e.has_descendant, children: []}
            });
          }
        )
        .catch(error => vi.mixinAlert("Unable to refresh folders list", true));
    }
  }
</script>

<style scoped>
  .item {
    cursor: pointer;
  }
</style>
