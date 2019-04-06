<template>
    <b-container>
        <b-row>
            <b-col>
                Upload document
            </b-col>
            <b-col md="8">
                <b-form-file
                        v-model="file"
                        :state="Boolean(file)"
                        placeholder="Choose a file..."
                        drop-placeholder="Drop file here..."
                ></b-form-file>
            </b-col>
            <b-col md="auto">
                <b-button variant="primary" :disabled="isUploading" @click="uploadDocument">Submit</b-button>
            </b-col>
        </b-row>
        <b-row align-h="center">
            <p>Response: {{ response }}</p>
        </b-row>
        <b-row align-h="center">
            <b-col cols="12">
                <b-progress :class="{ 'd-none': !isUploading }" max="100" :value="uploadProgress" variant="success"
                            show-progress/>
            </b-col>
        </b-row>

    </b-container>
</template>

<script>
    import axios from 'axios'

    export default {
        name: "FTLUpload",

        data() {
            return {
                file: null,
                response: '',
                uploading: false,
                uploadProgress: 0
            }
        },

        computed: {
            isUploading: function () {
                return this.uploading;
            }
        },

        methods: {
            uploadDocument: function () {
                let vi = this;
                vi.uploading = true;

                let formData = new FormData();
                formData.append('file', this.file);
                formData.append('json', '{}');  // No meta data to send for now

                // Pass CSRF token from cookie to XHR call header (handled by Axios)
                let axiosConfig = {
                    xsrfCookieName: 'csrftoken',
                    xsrfHeaderName: 'X-CSRFToken',
                    onUploadProgress: progressEvent => {
                        if (progressEvent.lengthComputable) {
                            vi.uploadProgress = progressEvent.loaded * 100 / progressEvent.total;
                        } else {
                            vi.uploadProgress = 100;
                        }
                    }
                };

                axios
                    .post('/app/api/v1/documents/upload', formData, axiosConfig)
                    .then(response => {
                        vi.$emit('newupload'); // Event for refresh documents list
                        vi.response = response.data;
                    })
                    .catch(error => vi.response = error)
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