<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <section>
    <b-row>
      <b-col cols="12" md="8">
        <b-form-file
          multiple
          ref="fileUploadField"
          v-model="files"
          :state="files.length > 0 || null"
          :placeholder="$t('Upload document')"
          :drop-placeholder="$t('Drop file here...')"
          :browse-text="$t('Browse')"
          :accept="exts.join(',')"
        ></b-form-file>
      </b-col>
      <b-col cols="12" md="2">
        <b-button
          class="w-100 mt-2 mt-md-0"
          id="upload-button"
          variant="primary"
          :disabled="uploading || !files.length > 0"
          @click="uploadDocument"
        >
          {{ $t("Upload") }}
        </b-button>
      </b-col>
      <b-col
        class="d-none d-md-flex align-items-center justify-content-center"
        md="2"
      >
        <a
          id="import-folder-link"
          class="text-center"
          href="https://welcome.papermatter.app/downloads"
          target="_blank"
          :title="
            $t(
              'Import a folder or a large amount of documents using the local import client'
            )
          "
        >
          {{ $t("Import a folder") }}
          <font-awesome-icon icon="external-link-alt" size="sm" />
        </a>
      </b-col>
    </b-row>
    <b-row class="mt-1">
      <b-col>
        <b-progress
          id="document-upload-loader"
          :class="{ 'd-none': !uploading }"
          :max="100"
          variant="success"
        >
          <b-progress-bar :value="globalUploadProgress">
            <strong>{{ globalUploadProgress.toFixed(0) }} %</strong>
          </b-progress-bar>
        </b-progress>
      </b-col>
    </b-row>
  </section>
</template>

<i18n>
  fr:
    Upload document: Ajouter un document
    Drop file here...: Déposer un fichier ici ...
    Browse: Parcourir
    Upload: Envoyer
    Import a folder: Importer un dossier
    Import a folder or a large amount of documents using the local import client: Importer un dossier ou un grand
      nombre de documents en utilisant le client d'import local
    Unable to create thumbnail: Erreur lors de la génération de la miniature
    Document uploaded: Document ajouté
    Could not upload document: Erreur lors de l'ajout du document
</i18n>
<script>
import axios from "axios";
import { createThumbFromFile } from "@/thumbnailGenerator";
import { axiosConfig } from "@/constants";
import { mapState } from "vuex";

export default {
  name: "FTLUpload",
  props: {
    currentFolder: {
      type: Object,
      required: false,
    },
  },

  data() {
    return {
      files: [],
      uploading: false,
      uploadedFilesCount: 0,
      currentUploadProgress: 0,
      globalUploadProgress: 0,
    };
  },

  computed: {
    exts: function () {
      const list_exts = [];

      for (const [k, v] of Object.entries(this.ftlAccount["supported_exts"])) {
        list_exts.push(v);
      }

      return list_exts;
    },
    ...mapState(["ftlAccount"]), // generate vuex computed getter
  },

  methods: {
    refreshUploadProgression: function (progressEvent) {
      let vi = this;
      if (progressEvent.lengthComputable) {
        vi.currentUploadProgress =
          (progressEvent.loaded * 100) / progressEvent.total;
      } else {
        vi.currentUploadProgress = 100;
      }

      vi.globalUploadProgress =
        (vi.currentUploadProgress + vi.uploadedFilesCount * 100) /
        vi.files.length;
    },

    uploadDocument: async function () {
      let vi = this;
      vi.uploading = true;
      // Non reactive copy, avoid uploading in wrong folder while the user is navigating.
      const folderForUpload = Object.assign({}, vi.currentFolder);

      for (const file of vi.files) {
        let formData = new FormData();
        // file binary
        formData.append("file", file);

        // parent folder
        let jsonData = {};
        if (folderForUpload != null) {
          jsonData = { ftl_folder: folderForUpload.id };
        }
        formData.append("json", JSON.stringify(jsonData));

        if (file.type === "application/pdf") {
          // thumbnail generation
          try {
            let thumb = await createThumbFromFile(file);
            formData.append("thumbnail", thumb);
          } catch (e) {
            vi.mixinAlert(this.$t("Unable to create thumbnail"), true);
          }
        }

        const updatedAxiosConfig = Object.assign({}, axiosConfig, {
          onUploadProgress: this.refreshUploadProgression,
        });
        await axios
          .post("/app/api/v1/documents/upload", formData, updatedAxiosConfig)
          .then((response) => {
            vi.$emit("event-new-upload", { doc: response.data }); // Event for refresh documents list
            vi.mixinAlert(this.$t("Document uploaded"));
          })
          .catch((error) =>
            vi.mixinAlert(this.$t("Could not upload document"), true)
          );
        vi.uploadedFilesCount++;
      }

      vi.files = [];
      vi.uploadedFilesCount = vi.currentUploadProgress = vi.globalUploadProgress = 0;
      vi.uploading = false;
    },
  },
};
</script>

<style scoped></style>
