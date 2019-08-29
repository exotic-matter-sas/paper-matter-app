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
        files: [],
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
        let formData = new FormData();

        vi.uploading = true;

        // start thumbnail generation
        vi.uploadProgress = 10;

        // TODO disable thumbnail generation on mobile
        for (let i = 0; i < vi.files.length; ++i) {
          formData.append('files[]', vi.files[i]);
          try {
            let thumb = await createThumbFromFile(vi.files[i]);
            formData.append('thumbs_' + i, thumb);
          } catch (e) {
            vi.mixinAlert("Error creating thumbnail", true);
          }
        }

        vi.uploadProgress = 20;
        let jsonData = {};

        if (vi.currentFolder != null) {
          jsonData = {'ftl_folder': vi.currentFolder.id};
        }

        formData.append('json', JSON.stringify(jsonData));

        const updatedAxiosConfig = Object.assign({}, axiosConfig, {onUploadProgress: this.refreshUploadProgression});

        axios
          .post('/app/api/v2/documents/upload', formData, updatedAxiosConfig)
          .then(response => {
            vi.$emit('event-new-upload', {docs: response.data}); // Event for refresh documents list
            vi.files = [];
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
