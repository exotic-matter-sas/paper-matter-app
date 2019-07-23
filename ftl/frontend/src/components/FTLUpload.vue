<template>
  <section>
    <b-row no-gutters>
      <b-col cols="12" md="10">
        <b-form-file
          ref="fileUploadField"
          v-model="file"
          :state="Boolean(file)"
          :placeholder="this.$_('Upload document')"
          :drop-placeholder="this.$_('Drop file here...')"
          :browse-text="this.$_('Browse')"
        ></b-form-file>
      </b-col>
      <b-col cols="12" md="2">
        <b-button class="w-100 mt-2 ml-0 mt-md-0 ml-md-2" id="upload-button" variant="primary" :disabled="uploading || !file" @click="uploadDocument">
          {{this.$_('Upload')}}
        </b-button>
      </b-col>
    </b-row>
    <b-row>
      <b-col>
        <b-progress id="document-upload-loader" :class="{ 'd-none': !uploading }" :max="100" :value="uploadProgress"
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
        file: null,
        response: '',
        uploading: false,
        uploadProgress: 0,
      }
    },

    methods: {
      refreshUploadProgression: function (progressEvent) {
        let vi = this;
        if (progressEvent.lengthComputable) {
          vi.uploadProgress = progressEvent.loaded * 100 / progressEvent.total;
        } else {
          vi.uploadProgress = 100;
        }
      },

      uploadDocument: async function () {
        let vi = this;
        let thumb64 = null;
        vi.uploading = true;

        // start thumbnail generation
        vi.uploadProgress = 10;
        // TODO disable thumbnail generation on mobile
        try {
          thumb64 = await createThumbFromFile(vi.file);
        } catch (e) {
          vi.mixinAlert("Error creating thumbnail", true);
          thumb64 = null;
        }

        vi.uploadProgress = 20;
        let jsonData = {};

        if (vi.currentFolder != null) {
          jsonData = {'ftl_folder': vi.currentFolder.id};
        }

        let formData = new FormData();

        if (thumb64 !== null) {
          formData.append('thumbnail', thumb64);
        }
        formData.append('file', this.file);
        formData.append('json', JSON.stringify(jsonData));

        const updatedAxiosConfig = Object.assign({}, axiosConfig, {onUploadProgress: this.refreshUploadProgression});

        axios
          .post('/app/api/v1/documents/upload', formData, updatedAxiosConfig)
          .then(response => {
            vi.$emit('event-new-upload'); // Event for refresh documents list
            vi.response = response.data;
            vi.file = "";
            vi.mixinAlert("Document uploaded");
          })
          .catch(error => vi.mixinAlert("Could not upload document", true))
          .then(function () {
            vi.uploadProgress = 0;
            vi.uploading = false;
          });
      }
    }
  }
</script>

<style scoped>

</style>
