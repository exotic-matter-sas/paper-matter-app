<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <section id="upload-section">
    <b-form-file
      id="upload-doc-input"
      class="d-none"
      multiple
      v-model="selectedFiles"
      :accept="exts.join(',')"
      @input="addUploadTask"
    ></b-form-file>
    <b-row>
      <FTLUploadTask
        class="mt-3"
        v-for="(task, folderId) in uploadTasks"
        :key="folderId"
        :folder-name="task.folderName"
        :left-to-upload="task.files.length"
        :successes-count="uploadTasksCompleted[folderId].successes.length"
        :errors-count="uploadTasksCompleted[folderId].errors.length"
        @event-interrupt-task="$set(uploadTasksInterrupted, folderId, true)"
      />
    </b-row>
  </section>
</template>

<i18n>
  fr:
    Root: Racine
    Upload document: Ajouter un document
    Drop file here...: Déposer un fichier ici ...
    Browse: Parcourir
    Upload: Envoyer
    Unable to create thumbnail: Erreur lors de la génération de la miniature
    Document uploaded: Document ajouté
    "| (and 1 skipped) | (and {n} skipped)": "| (et 1 ignoré) | (et {n} ignorés)"
    "| 1 document added into {folderName} | {n} documents added into {folderName}": "| 1 document ajouté dans {folderName} | {n} documents ajoutés dans {folderName}"
    "| 1 document couldn't be added into {folderName} | {n} documents couldn't be added into {folderName}": "| 1 document n'a pu être ajouté dans {folderName} | {n} documents n'ont pu être ajoutés dans {folderName}"
    "| 1 document added | {n} documents added": "| 1 document ajouté | {n} documents ajoutés"
    "| another couldn't be added | {n} others couldn't be added": "| 1 autre n'a pu être ajouté | {n} autres n'ont pu être ajoutés"
    "{successesMention} into {folderName}, {errorsMention}.": "{successesMention} dans {folderName}, {errorsMention}."
</i18n>

<script>
import axios from "axios";
import { createThumbFromFile } from "@/thumbnailGenerator";
import { axiosConfig } from "@/constants";
import { mapGetters, mapState } from "vuex";
import FTLUploadTask from "@/components/FTLUploadTask";

export default {
  name: "FTLUpload",
  components: { FTLUploadTask },
  data() {
    return {
      selectedFiles: [],
      uploadTasks: {},
      uploadTasksCompleted: {},
      uploadTasksInterrupted: {},
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
    ...mapGetters(["getCurrentFolder"]), // generate vuex computed getter
  },

  methods: {
    addUploadTask: function () {
      const uploadFolderId = this.getCurrentFolder === null ? null : this.getCurrentFolder.id;
      const folderName = this.getCurrentFolder === null ? this.$t('Root') : this.getCurrentFolder.name;

      // if there is already an upload task for this folder add selectedFiles to the file to upload
      if (uploadFolderId in this.uploadTasks) {
        this.uploadTasks[uploadFolderId].files.push(...this.selectedFiles);
      }
      else {
        this.$set(this.uploadTasksCompleted, uploadFolderId, {
          folderName: folderName,
          successes: [],
          errors: []
        });
        this.$set(this.uploadTasks, uploadFolderId, {
          folderName: folderName,
          files: this.selectedFiles
        });
      }
      this.selectedFiles = [];

      if (!this.uploading) {
        this.consumeUploadTasks();
      }
    },

    consumeUploadTasks: async function () {
      this.uploading = true;
      let folderId;
      let files;
      let fileToUpload;
      let folderName;
      let entries = Object.entries(this.uploadTasks);
      let uploadTaskSuccesses;
      let uploadTaskErrors;

      while (entries.length > 0) {
        // get first upload task
        [folderId, {folderName, files}] = entries[0];
        uploadTaskSuccesses = this.uploadTasksCompleted[folderId].successes;
        uploadTaskErrors = this.uploadTasksCompleted[folderId].errors;

        while (files.length > 0 && !(folderId in this.uploadTasksInterrupted)) {
          fileToUpload = files[0];
          await this.uploadDocument(folderId, fileToUpload)
            // push file path to successes or full file object to errors (to allow later retry)
            .then(() => uploadTaskSuccesses.push(fileToUpload.path))
            .catch(() => uploadTaskErrors.push(fileToUpload))
            // consume file
            .finally(() => files.shift());
        }

        // notify user
        this.notifyUploadTaskCompleted(folderName, uploadTaskSuccesses.length, uploadTaskErrors.length, files.length);
        // consume uploadTask
        this.$delete(this.uploadTasks, folderId);
        // consume interrupted flag
        folderId in this.uploadTasksInterrupted ? this.$delete(this.uploadTasksInterrupted, folderId) : undefined;

        // refresh entries
        entries = Object.entries(this.uploadTasks);
      }
      this.uploading = false;
    },

    uploadDocument: async function (folderId, file) {
      let vi = this;

      let formData = new FormData();
      // file binary
      formData.append("file", file);

      // parent folder
      let jsonData = {};
      if (folderId !== "null") {
        jsonData = { ftl_folder: folderId };
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

      return await axios
        .post("/app/api/v1/documents/upload", formData, axiosConfig)
        .then((response) => {
          vi.$emit("event-new-upload", { doc: response.data }); // Event for refresh documents list
        })
    },

    notifyUploadTaskCompleted: function(folderName, successesCount, errorsCount, skippedCount) {
      folderName = folderName === null ? this.$('Root') : folderName;
      console.log("skippedCount", skippedCount);
      const skippedMention = skippedCount > 0 ?
        this.$tc("| (and 1 skipped) | (and {n} skipped)", skippedCount) : "";

      // Only successes
      if (successesCount > 0 && errorsCount === 0) {
        this.mixinAlert(this.$tc("| 1 document added into {folderName} | {n} documents added into {folderName}",
          successesCount, {folderName}) + ` ${skippedMention}`);
      }
      // Only errors
      else if (errorsCount > 0 && successesCount === 0) {
        this.mixinAlert(this.$tc("| 1 document couldn't be added into {folderName} | {n} documents couldn't be added into {folderName}",
          errorsCount, {folderName}) + ` ${skippedMention}`,
          true);
      }
      // Mixed successes and errors
      else if (successesCount > 0 && errorsCount > 0) {
        const successesMention = this.$tc("| 1 document added | {n} documents added", successesCount);
        const errorsMention = this.$tc("| another couldn't be added | {n} others couldn't be added", errorsCount);
        this.mixinAlertWarning(this.$t("{successesMention} into {folderName}, {errorsMention}.",
          {successesMention, folderName, errorsMention}) + ` ${skippedMention}`);
      }

    }
  },
};
</script>

<style scoped></style>
