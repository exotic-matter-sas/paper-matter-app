<template>
    <b-container>
        <b-row>
            <b-col>
                {{this.$_('Upload document')}}
            </b-col>
            <!--            <b-col v-show="this.thumbnail">-->
            <!--                <img :src="this.thumbnail"/>-->
            <!--            </b-col>-->
            <b-col md="8">
                <b-form-file
                    ref="fileUploadField"
                    v-model="file"
                    :state="Boolean(file)"
                    :placeholder="this.$_('Choose a file...')"
                    :drop-placeholder="this.$_('Drop file here...')"
                    :browse-text="this.$_('Browse')"
                ></b-form-file>
            </b-col>
            <b-col md="auto">
                <b-button id="upload-button" variant="primary" :disabled="uploading || !file" @click="uploadDocument">
                    {{this.$_('Upload')}}
                </b-button>
            </b-col>
        </b-row>
        <b-row align-h="center">
            <b-col cols="12">
                <b-progress :class="{ 'd-none': !uploading }" :max="100" :value="uploadProgress" variant="success"
                            show-progress/>
            </b-col>
        </b-row>

    </b-container>
</template>

<script>
    import pdfjsLib from 'pdfjs-dist'
    import axios from 'axios'

    pdfjsLib.disableWorker = true;
    window.URL = window.URL || window.webkitURL;

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
                thumbnail: null
            }
        },

        methods: {
            createThumb: function (file) {
                const vi = this;
                return new Promise((resolve, reject) => {
                    let objectURL = window.URL.createObjectURL(file);

                    pdfjsLib.getDocument(objectURL).then(function (pdf) {
                        pdf.getPage(1).then(function (page) {
                            const canvas = document.createElement("canvas");
                            const context = canvas.getContext('2d');

                            let viewport = page.getViewport(0.5);

                            canvas.height = viewport.height;
                            canvas.width = viewport.width;

                            page.render({
                                canvasContext: context,
                                viewport: viewport
                            }).then(function () {
                                vi.thumbnail = canvas.toDataURL();
                                resolve(vi.thumbnail);
                            });
                        }).catch(function () {
                            reject("pdf thumb error: could not open page 1 of document " + filePath + ". Not a pdf ?");
                        });
                    }).catch(function () {
                        reject("pdf thumb error: could not find or open document " + filePath + ". Not a pdf ?");
                    });
                });
            },

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
                try {
                    thumb64 = await vi.createThumb(vi.file);
                } catch (e) {
                    // TODO error
                    return;
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

                // Pass CSRF token from cookie to XHR call header (handled by Axios)
                let axiosConfig = {
                    xsrfCookieName: 'csrftoken',
                    xsrfHeaderName: 'X-CSRFToken',
                    onUploadProgress: this.refreshUploadProgression
                };

                axios
                    .post('/app/api/v1/documents/upload', formData, axiosConfig)
                    .then(response => {
                        vi.$emit('event-new-upload'); // Event for refresh documents list
                        vi.response = response.data;
                        vi.file = "";
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
