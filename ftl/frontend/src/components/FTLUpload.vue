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
    "| Sorry, this file can't be added due to its unsupported type. | Sorry, these files can't be added due to their unsupported types.": "| Désolé, ce fichier ne peut être ajouté car son type n'est pas supporté. | Désolé, ces fichiers ne peuvent être ajoutés car leurs types ne sont pas supportés."
    "| One file has been ignored due to its unsupported type | {n} files have been ignored due to their unsupported types": "| Un fichier a été ignoré car son type n'est pas supporté | {n} fichiers ont été ignorés car leurs types n'est pas supporté"
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

  props: {
    filesToUpload: {
      type: Array,
      default: () => [],
    },
  },

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

  watch: {
    filesToUpload: function (newVal, oldVal) {
      if (newVal.length > 0) {
        this.addUploadTask(newVal);
        // reset filesToUpload
        this.$emit("update:filesToUpload", []);
      }
    },
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
    addUploadTask: function (filesToUpload = null) {
      // if no filesToUpload is passed, use input selectedFiles as source
      let files =
        filesToUpload === null
          ? this.selectedFiles
          : // filesToUpload need to be filtered (eg. when it comes for drag n dropped files)
            filesToUpload.filter(
              (file) => file.type in this.ftlAccount["supported_exts"]
            );

      if (files.length > 0) {
        // Convert the id to string to use it as an object key
        // (recent browsers preserve attribute insertion order in object when the specified key is a string)
        const uploadFolderIdKey =
          this.getCurrentFolder === null
            ? "id-null"
            : `id-${this.getCurrentFolder.id}`;
        const folderName =
          this.getCurrentFolder === null
            ? this.$t("Root")
            : this.getCurrentFolder.name;

        // If there is already an existing upload task for this folder append files to it
        if (uploadFolderIdKey in this.uploadTasks) {
          this.uploadTasks[uploadFolderIdKey].files.push(...files);
        }
        // Create new entry in uploadTasks and uploadTasksCompleted
        else {
          if (!(uploadFolderIdKey in this.uploadTasksCompleted)) {
            this.$set(this.uploadTasksCompleted, uploadFolderIdKey, {
              folderName,
              successes: [],
              errors: [],
            });
          }

          this.$set(this.uploadTasks, uploadFolderIdKey, {
            folderName,
            files: files,
          });
        }

        // reset selectedFiles if files where added from it
        if (filesToUpload === null) {
          this.selectedFiles = [];
        }
        // warn user if some files have been ignored due to their types
        else {
          const ignoredFilesCount = filesToUpload.length - files.length;
          if (ignoredFilesCount > 0) {
            this.mixinAlertWarning(
              this.$tc(
                "| One file has been ignored due to its unsupported type | {n} files have been ignored due to their unsupported types",
                ignoredFilesCount
              )
            );
          }
        }

        if (!this.uploading) {
          this.consumeUploadTasks();
        }
      } else if (filesToUpload.length > 0) {
        this.mixinAlert(
          this.$tc(
            "| Sorry, this file can't be added due to its unsupported type. | Sorry, these files can't be added due to their unsupported types.",
            filesToUpload.length
          ),
          true
        );
      }
    },

    consumeUploadTasks: async function () {
      this.uploading = true;
      let folderIdKey;
      let folderId;
      let files;
      let fileToUpload;
      let folderName;
      let entries = Object.entries(this.uploadTasks);
      let uploadTaskSuccesses;
      let uploadTaskErrors;

      while (entries.length > 0) {
        // get first upload task
        [folderIdKey, { folderName, files }] = entries[0];
        folderId =
          folderIdKey.slice(3) === "null"
            ? null
            : parseInt(folderIdKey.slice(3)); // remove "id-" prefix and convert to null or int
        uploadTaskSuccesses = this.uploadTasksCompleted[folderIdKey].successes;
        uploadTaskErrors = this.uploadTasksCompleted[folderIdKey].errors;

        while (
          files.length > 0 &&
          !(folderIdKey in this.uploadTasksInterrupted)
        ) {
          fileToUpload = files[0];
          await this.uploadDocument(folderId, fileToUpload)
            // push file path to successes or full file object to errors (to allow later retry)
            .then(() => uploadTaskSuccesses.push(fileToUpload.path))
            .catch(() => uploadTaskErrors.push(fileToUpload))
            // consume file
            .finally(() => files.shift());
        }

        // notify user
        this.notifyUploadTaskCompleted(
          folderName,
          uploadTaskSuccesses.length,
          uploadTaskErrors.length,
          files.length
        );
        // consume uploadTask
        this.$delete(this.uploadTasks, folderIdKey);
        // consume interrupted flag
        folderIdKey in this.uploadTasksInterrupted
          ? this.$delete(this.uploadTasksInterrupted, folderIdKey)
          : undefined;

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
        });
    },

    notifyUploadTaskCompleted: function (
      folderName,
      successesCount,
      errorsCount,
      skippedCount
    ) {
      folderName = folderName === null ? this.$("Root") : folderName;
      const skippedMention =
        skippedCount > 0
          ? this.$tc("| (and 1 skipped) | (and {n} skipped)", skippedCount)
          : "";

      // Only successes
      if (successesCount > 0 && errorsCount === 0) {
        this.mixinAlert(
          this.$tc(
            "| 1 document added into {folderName} | {n} documents added into {folderName}",
            successesCount,
            { folderName }
          ) + ` ${skippedMention}`
        );
      }
      // Only errors
      else if (errorsCount > 0 && successesCount === 0) {
        this.mixinAlert(
          this.$tc(
            "| 1 document couldn't be added into {folderName} | {n} documents couldn't be added into {folderName}",
            errorsCount,
            { folderName }
          ) + ` ${skippedMention}`,
          true
        );
      }
      // Mixed successes and errors
      else if (successesCount > 0 && errorsCount > 0) {
        const successesMention = this.$tc(
          "| 1 document added | {n} documents added",
          successesCount
        );
        const errorsMention = this.$tc(
          "| another couldn't be added | {n} others couldn't be added",
          errorsCount
        );
        this.mixinAlertWarning(
          this.$t("{successesMention} into {folderName}, {errorsMention}.", {
            successesMention,
            folderName,
            errorsMention,
          }) + ` ${skippedMention}`
        );
      }
    },
  },
};
</script>

<style scoped></style>
