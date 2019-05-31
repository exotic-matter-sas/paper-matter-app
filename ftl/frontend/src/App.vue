<template>
    <div id="app" class="m-0">
        <header>
            <b-container fluid class="p-0">
                <FTLNavbar :account="account" @event-search="refreshDocumentWithSearch"
                           @event-clear-search="clearSearch"/>
            </b-container>
        </header>

        <section>
            <b-container>
                <b-row>
                    <b-col>
                        <FTLUpload :currentFolder="getCurrentFolder" @event-new-upload="updateDocument"/>
                    </b-col>
                </b-row>
                <b-row>
                    <b-col>
                        <b-button id="generate-thumb" variant="primary" class="m-1" @click="generateMissingThumbnail">
                            {{this.$_('Generate missing thumb')}}
                        </b-button>
                        <b-button id="refresh-documents" variant="primary" class="m-1" @click="updateDocument">
                            {{this.$_('Refresh documents list')}}
                        </b-button>
                        {{ this.$_('Last refresh') }} {{ lastRefreshFormatted }}
                    </b-col>
                </b-row>
            </b-container>
        </section>

        <section>
            <b-container>
                <b-row>
                    <b-button variant="primary" class="m-1" v-if="previousLevels.length"
                              @click="changeToPreviousFolder">
                        Up
                    </b-button>
                    <b-button v-else variant="primary" class="m-1" disabled>Up</b-button>
                    <FTLFolder v-for="folder in folders" :key="folder.id" :folder="folder"
                               @event-change-folder="changeFolder"/>
                    <b-button id="create-folder" class="m-1" variant="outline-primary" size="sm"
                              @click.prevent="newFolderModal = true">
                        {{ this.$_('Create new folder') }}
                    </b-button>
                </b-row>
            </b-container>
        </section>

        <section>
            <b-container>
                <b-row v-if="docLoading">
                    <b-col>
                        <b-spinner id="document-list-loader" style="width: 3rem; height: 3rem;" class="m-5"
                                   label="Loading..."></b-spinner>
                    </b-col>
                </b-row>
                <b-row align-h="around" v-else-if="docs.length">
                    <FTLDocument v-for="doc in docs" :key="doc.pid" :doc="doc" @event-delete-doc="updateDocument"
                                 @event-open-doc="openDocument"/>
                </b-row>
                <b-row v-else>
                    <b-col>{{ this.$_('No document yet') }}</b-col>
                </b-row>
            </b-container>
        </section>

        <footer>
            <b-container>
                <b-row>
                    <b-col>
                        {{ this.$_('ftl-app, open source software. Made with ❤ by ') }} <a
                        href="https://www.exotic-matter.fr">Exotic Matter</a>.
                    </b-col>
                </b-row>
            </b-container>
        </footer>

        <!-- Pdf viewer popup -->
        <div v-if="docModal" class="doc-view-modal" :class="{open: docModal}">
            <b-container>
                {{ this.$_('Title') }} {{ currentOpenDoc.title }}
            </b-container>
            <b-container>
                <b-row scr>
                    <b-col md="8">
                        <div class="embed-responsive embed-responsive-1by1 doc-pdf ">
                            <iframe v-if="currentOpenDoc.pid" class="embed-responsive-item"
                                    :src="`/assets/pdfjs/web/viewer.html?file=/app/uploads/` + currentOpenDoc.pid + `#search=` + currentSearch">
                            </iframe>
                        </div>

                    </b-col>
                    <b-col>
                        <b-row>AAA</b-row>
                        <b-row>BBB</b-row>
                        <b-row>CCC</b-row>
                    </b-col>
                </b-row>
            </b-container>
            <b-container>
                <b-row align-h="end">
                    <b-col cols="2">
                        <b-button variant="secondary" @click="docModal = false">{{this.$_('Close')}}</b-button>
                    </b-col>
                </b-row>
            </b-container>
        </div>

        <b-modal v-if="newFolderModal" v-model="newFolderModal" @ok="createNewFolder"
                 :ok-disabled="newFolderName === ''"
                 :cancel-title="this.$_('Cancel')"
                 :ok-title="this.$_('Create')">
            <span slot="modal-title">{{ this.$_('Create a new folder') }}</span>
            <b-container>
                <!-- TODO add current folder name to title -->
                <b-form-group
                    id="fieldset-new-folder"
                    :description="this.$_('The name of the folder')"
                    :label="this.$_('The folder will be created in the current folder.')"
                    label-for="new-folder">
                    <b-form-input id="new-folder" v-model="newFolderName" trim></b-form-input>
                </b-form-group>
            </b-container>
        </b-modal>
    </div>
</template>

<script>
    import FTLNavbar from './components/FTLNavbar'
    import FTLFolder from './components/FTLFolder'
    import FTLDocument from './components/FTLDocument'
    import FTLUpload from './components/FTLUpload'
    import axios from 'axios'
    import qs from 'qs'
    import {createThumbFromUrl} from "./thumbnailGenerator";
    import {axiosConfig} from "./constants";

    export default {
        name: 'app',
        components: {
            FTLNavbar,
            FTLFolder,
            FTLDocument,
            FTLUpload
        },

        data() {
            return {
                // Misc account stuff
                account: {},

                // Documents list
                docs: [],
                docPid: null,
                docModal: false,
                lastRefresh: Date.now(),
                currentSearch: "",
                docLoading: false,

                // Folders list and breadcrumb
                folders: [],
                previousLevels: [],

                // Create folder data
                newFolderName: '',
                newFolderModal: false,

                // PDF viewer
                currentOpenDoc: {title: 'loading'},
                publicPath: process.env.BASE_URL
            }
        },

        mounted() {
            // get account value from Django core/home.html template
            let ftlAccountElem = document.getElementById('ftlAccount');
            if (ftlAccountElem) {
                this.account = JSON.parse(ftlAccountElem.textContent);
            }
            this.changeFolder();
        },

        computed: {
            lastRefreshFormatted: function () {
                return new Date(this.lastRefresh);
            },

            getCurrentFolder: function () {
                if (this.previousLevels.length) {
                    return this.previousLevels[this.previousLevels.length - 1];
                } else {
                    return null;
                }
            },
        },

        methods: {
            refreshFolders: function () {
                this.updateFolder(this.getCurrentFolder);
            },

            changeFolder: function (folder = null) {
                if (folder) this.previousLevels.push(folder);
                this.currentSearch = "";
                this.updateFolder(folder);
                this.updateDocument();
            },

            changeToPreviousFolder: function () {
                this.previousLevels.pop(); // Remove current level
                let level = this.getCurrentFolder;
                this.currentSearch = "";
                this.updateFolder(level);
                this.docs = []; // Clear docs when changing folder to avoid display artefact
                this.updateDocument();
            },

            openDocument: function (pid) {
                this.docPid = pid;
                this.docModal = true;

                const vi = this;
                axios
                    .get('/app/api/v1/documents/' + pid)
                    .then(response => {
                        vi.currentOpenDoc = response.data;

                        if (!response.data.thumbnail_available) {
                            vi.createThumbnailForDocument(response.data);
                        }

                    }).catch(error => vi.mixinAlert("Unable to show document.", true));
            },

            createThumbnailForDocument: async function (doc) {
                const vi = this;
                let thumb64;

                try {
                    thumb64 = await createThumbFromUrl('/app/uploads/' + doc.pid);
                } catch (e) {
                    vi.mixinAlert("Unable to update thumbnail", true);
                    return;
                }

                let jsonData = {'thumbnail_binary': thumb64};


                axios.patch('/app/api/v1/documents/' + doc.pid, jsonData, axiosConfig)
                    .then(response => {
                        vi.mixinAlert("Thumbnail updated!");
                        vi.updateDocument();
                    }).catch(error => vi.mixinAlert("Unable to update thumbnail", true));
            },

            refreshDocumentWithSearch: function (text) {
                this.currentSearch = text;
                this.updateDocument();
            },

            clearSearch: function () {
                this.refreshDocumentWithSearch("");
            },

            updateDocument: function () {
                const vi = this;
                let queryString = {};

                if (vi.previousLevels.length > 0) {
                    queryString['level'] = this.getCurrentFolder.id;
                }

                if (vi.currentSearch !== null && vi.currentSearch !== "") {
                    queryString['search'] = vi.currentSearch;
                }

                let strQueryString = '?' + qs.stringify(queryString);

                this.docLoading = true;

                axios
                    .get('/app/api/v1/documents/' + strQueryString)
                    .then(response => {
                        this.docLoading = false;
                        vi.docs = response.data['results'];
                        vi.lastRefresh = Date.now();
                    }).catch(error => {
                    this.docLoading = false;
                    vi.mixinAlert("Unable to refresh documents list.", true);
                });
            },

            updateFolder: function (level = null) {
                const vi = this;
                let qs = '';

                // While loading folders, clear folders to avoid showing current sets of folders intermittently
                vi.folders = [];

                if (level) {
                    qs = '?level=' + level.id;
                }

                axios
                    .get("/app/api/v1/folders/" + qs)
                    .then(response => {
                        vi.folders = response.data;
                    }).catch(error => vi.mixinAlert("Unable to refresh folders list", true));
            },

            createNewFolder: function () {
                const vi = this;
                let parent = null;

                if (vi.previousLevels.length > 0) {
                    parent = vi.previousLevels[vi.previousLevels.length - 1].id;
                }

                let postBody = {name: vi.newFolderName, parent: parent};

                axios
                    .post("/app/api/v1/folders/", postBody, axiosConfig)
                    .then(() => {
                        // TODO flash the new folder when just created
                        vi.newFolderName = '';
                        vi.refreshFolders();
                    }).catch(error => vi.mixinAlert("Unable to create new folder.", true));
            },

            generateMissingThumbnail: function () {
                const vi = this;
                vi.mixinAlert("Updating thumbnail");

                axios.get("/app/api/v1/documents?flat=true")
                    .then(async response => {
                        let documents = response.data;

                        while (documents !== null && documents.results.length > 0) {
                            for (const doc of documents.results) {
                                if (doc['thumbnail_available'] === false) {
                                    let thumb64;

                                    try {
                                        thumb64 = await createThumbFromUrl('/app/uploads/' + doc.pid);
                                    } catch (e) {
                                        vi.mixinAlert("Unable to update thumbnail", true);
                                        continue;
                                    }

                                    let jsonData = {'thumbnail_binary': thumb64};

                                    axios.patch('/app/api/v1/documents/' + doc.pid, jsonData, axiosConfig)
                                        .then(response => {
                                            vi.mixinAlert("Thumbnail updated! " + doc.pid);
                                        }).catch(error => vi.mixinAlert("Unable to update thumbnail " + doc.pid, true));
                                }
                            }

                            if (documents.next == null) {
                                documents = null;
                            } else {
                                let resp = await axios.get(documents.next);
                                documents = await resp.data;
                            }
                        }
                    })
                    .catch(error => {
                        vi.mixinAlert("An error occurred while updating thumbnail", true)
                    })
                    .then(() => {
                        vi.mixinAlert("Finished updating thumbnail");
                    });
            }
        }
    }
</script>

<style>
    #app {
        font-family: 'Avenir', Helvetica, Arial, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        text-align: center;
        color: #2c3e50;
        margin-top: 60px;
    }

    /* PDF.js viewer custom css */
    .doc-view-modal {
        display: none;
        height: 100%;
        left: 0;
        position: fixed;
        top: 0;
        width: 100%;
        background: white;
        z-index: 1000;
        padding: 20px;
    }

    .doc-view-modal {
        display: flex;
        flex-direction: column;
    }

    .doc-pdf {
        padding-top: 100%;
    }

    /* Temp for viewing layout */
    div {
        border: 1px dotted;
    }
</style>
