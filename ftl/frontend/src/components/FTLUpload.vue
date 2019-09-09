<template>
  <section>
    <b-row>
      <b-col cols="12" md="10">
        <b-form-file
          multiple
          ref="fileUploadField"
          v-model="files"
          :state="files.length > 0"
          :placeholder="this.$_('Upload document')"
          :drop-placeholder="this.$_('Drop file here...')"
          :browse-text="this.$_('Browse')"
          accept="application/pdf"
        ></b-form-file>
      </b-col>
      <b-col cols="12" md="2">
        <b-button class="w-100 mt-2 mt-md-0" id="upload-button" variant="primary"
                  :disabled="uploading || !files.length > 0"
                  @click="uploadDocument">
          {{this.$_('Upload')}}
        </b-button>
      </b-col>
    </b-row>
    <b-row>
      <b-col>
        <b-progress id="document-upload-loader" :class="{ 'd-none': !uploading }" :max="100" :value="globalUploadProgress"
                    variant="success"
                    show-progress/>
      </b-col>
    </b-row>
  </section>
</template>

<script>
  import axios from 'axios';
  import {createThumbFromFile} from "@/thumbnailGenerator";
  import {axiosConfig} from "@/constants";

  export default {
    name: "FTLUpload",
    props: {
      currentFolder: {
        type: Object,
        required: false
      }
    },

    data() {
      return {
        files: [],
        uploading: false,
        uploadedFilesCount: 0,
        currentUploadProgress: 0,
        globalUploadProgress: 0,
      }
    },

    methods: {
      refreshUploadProgression: function (progressEvent) {
        let vi = this;
        if (progressEvent.lengthComputable) {
          vi.currentUploadProgress = progressEvent.loaded * 100 / progressEvent.total;
        } else {
          vi.currentUploadProgress = 100;
        }

        vi.globalUploadProgress = (vi.currentUploadProgress + vi.uploadedFilesCount * 100) / vi.files.length;
      },

      uploadDocument: async function () {
        let vi = this;
        vi.uploading = true;

        for (const file of vi.files) {
          let formData = new FormData();
          // file binary
          formData.append('file', file);

          // parent folder
          let jsonData = {};
          if (vi.currentFolder != null) {
            jsonData = {'ftl_folder': vi.currentFolder.id};
          }
          formData.append('json', JSON.stringify(jsonData));

          // thumbnail generation (skipped on mobile)
          if (!navigator.userAgent.toLowerCase().includes("mobi")){
            try {
              let thumb = await createThumbFromFile(file);
              formData.append('thumbnail', thumb);
            } catch (e) {
              vi.mixinAlert("Error creating thumbnail", true);
            }
          }

          const updatedAxiosConfig = Object.assign({}, axiosConfig, {onUploadProgress: this.refreshUploadProgression});
          await axios
            .post('/app/api/v1/documents/upload', formData, updatedAxiosConfig)
            .then(response => {
              vi.$emit('event-new-upload', {doc: response.data}); // Event for refresh documents list
              vi.mixinAlert("Document uploaded");
            })
            .catch(error => vi.mixinAlert("Could not upload document", true));
          vi.uploadedFilesCount++;
        }

        vi.files = [];
        vi.uploadedFilesCount = vi.currentUploadProgress = vi.globalUploadProgress = 0;
        vi.uploading = false;
      }
    }
  }
</script>

<style scoped>

</style>
