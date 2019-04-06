<template>
    <div class="upload">Upload document
        <label>
            <input type="file" id="file" ref="file" @change="handleFileUpload"/>
        </label>
        <button @click="uploadDocument">Submit</button>
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
                file: '',
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