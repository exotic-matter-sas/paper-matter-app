<template>
  <b-row>
    <b-col>
      <ul id="moving-folders">
        <FTLTreeItem
          class="item"
          v-for="folder in folders"
          :key="folder.id"
          :item="folder"
          :source-folder="sourceFolder">
        </FTLTreeItem>
      </ul>
    </b-col>
  </b-row>
</template>

<script>
  import FTLTreeItem from "@/components/FTLTreeItem";
  import axios from 'axios';

  export default {
    name: 'FTLTreeFolders',
    components: {
      FTLTreeItem
    },
    props: {
      start: Number,
      root: {type: Boolean, default: true},
      sourceFolder: Number
    },

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
            if (!vi.root) {
              // Add a static root
              vi.folders.push({id: null, name: vi.$_('Root')});
            }

            vi.folders = vi.folders
              .concat(
                response.data
                  .filter(function (e) {
                    return e.id !== vi.sourceFolder;
                  })
                  .map(function (e) {
                    return {id: e.id, name: e.name, has_descendant: e.has_descendant, children: []}
                  })
              );
          }
        )
        .catch(error => vi.mixinAlert(vi.$_('Unable to refresh folders list'), true));
    }
  }
</script>

<style scoped>
  .item {
    cursor: pointer;
  }

  .selected {
    background: dodgerblue;
  }
</style>
