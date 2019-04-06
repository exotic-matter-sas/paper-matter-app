<template>
    <div class="upload">Upload document

        <b-form-file
                v-model="file"
                :state="Boolean(file)"
                placeholder="Choose a file..."
                drop-placeholder="Drop file here..."
                @change="handleFileUpload"
        ></b-form-file>
        <div class="mt-3">Selected file: {{ file ? file.name : '' }}</div>

        <b-button variant="primary" @click="uploadDocument">Submit</b-button>

        <p>Response: {{ response }}</p>
        <p>Progress: {{ uploadProgress }}%</p>
    </div>
</template>

<script>
    import axios from 'axios'

    export default {
        name: "FTLUpload",

        data() {
            return {
                file: null,
                response: '',
                uploadProgress: null
            }
        },

        methods: {
            uploadDocument: function () {
                let vi = this;

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
                            vi.uploadProgress = '';
                        }
                    }
                };

                axios
                    .post('/app/api/v1/documents/upload', formData, axiosConfig)
                    .then(response => {
                        vi.$emit('newupload'); // Event for refresh documents list
                        vi.response = response.data;
                    })
                    .catch(error => vi.response = error);
            },

            handleFileUpload: function () {
                this.file = this.$refs.file.files[0];
            }
        }
    }
</script>

<style scoped>

</style>