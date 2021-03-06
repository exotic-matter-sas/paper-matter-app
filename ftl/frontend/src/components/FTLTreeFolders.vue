<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the Business Source License. See LICENSE at project root for more information.
  -->

<template>
  <b-row>
    <b-col id="moving-folders">
      <ul
        class="pl-0"
        v-if="folders.length > 0 && folders[0].children.length > 0"
      >
        <FTLTreeItem
          class="item"
          v-for="folder in folders"
          :key="folder.id"
          :item="folder"
          :folder-to-disable="folderToDisable"
          :folder-to-disable-message="folderToDisableMessage"
          :folder-to-hide="folderToHide"
        ></FTLTreeItem>
      </ul>
      <ul class="pl-0" v-else-if="lastFolderListingFailed">
        <li class="text-danger">
          {{ $t("Folders can't be loaded") }}
        </li>
      </ul>
      <ul class="pl-0" v-else>
        <li class="text-muted">
          {{ $t("No folder created yet") }}
        </li>
      </ul>
    </b-col>
  </b-row>
</template>

<i18n>
  fr:
    No folder created yet: Vous n'avez pas encore créé de dossier
    Folders can't be loaded: Les dossiers n'ont pu être chargés
    Root: Racine
</i18n>

<script>
import FTLTreeItem from "@/components/FTLTreeItem";
import axios from "axios";

export default {
  name: "FTLTreeFolders",
  components: {
    FTLTreeItem,
  },
  props: {
    // to disable a folder selection
    folderToDisable: { default: -1 },
    // to display an informative message next to the disabled folder
    folderToDisableMessage: { type: String, default: null },
    // to hide a folder from the list (eg. when moving a folder it can't be move to itself or one of its child)
    folderToHide: { default: -1 },
  },

  data() {
    return {
      folders: [],
      lastFolderListingFailed: false,
    };
  },

  mounted() {
    const vi = this;
    vi.lastFolderListingFailed = false;

    axios
      .get("/app/api/v1/folders")
      .then((response) => {
        let rootFolder = {
          id: null,
          name: vi.$t("Root"),
          has_descendant: true,
          is_root: true,
        };
        rootFolder.children = response.data
          .filter(function (e) {
            return e.id !== vi.folderToHide;
          })
          .map(function (e) {
            return {
              id: e.id,
              name: e.name,
              has_descendant: e.has_descendant,
              children: [],
            };
          });
        vi.folders.push(rootFolder);
      })
      .catch((error) => (vi.lastFolderListingFailed = true));
  },
};
</script>

<style scoped>
ul {
  list-style: none;
  margin-bottom: 0;
  user-select: none;
}

.item {
  cursor: pointer;
}
</style>
