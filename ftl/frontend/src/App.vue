<template>
    <div id="app" class="m-0">
        <header>
            <b-container fluid class="p-0">
                <FTLNavbar :account="account"/>
            </b-container>

            <b-alert
                    :variant="alertType"
                    dismissible
                    fade
                    :show="showAlert"
                    @dismissed="showAlert=false">
                {{ alertMessage }}
            </b-alert>
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
                        <b-button id="refresh-documents" variant="primary" @click="updateDocument">
                            {{ _('Refresh documents list') }}
                        </b-button>
                        {{ _('Last refresh') }} {{ lastRefreshFormatted }}
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
                    <b-button class="m-1" variant="outline-primary" size="sm" @click.prevent="newFolderModal = true">
                        {{ _('Create new folder') }}
                    </b-button>
                </b-row>
            </b-container>
        </section>

        <section>
            <b-container>
                <b-row align-h="around" v-if="docs.length">
                    <FTLDocument v-for="doc in docs" :key="doc.pid" :doc="doc" @event-delete-doc="updateDocument"
                                 @event-open-doc="openDocument"/>
                </b-row>
                <b-row v-else>
                    <b-col>{{ _('No document yet') }}</b-col>
                </b-row>
            </b-container>
        </section>

        <footer>
            <b-container>
                <b-row>
                    <b-col>
                        {{ _('ftl-app, open source software. Made with ❤ by ') }} <a href="https://www.exotic-matter.fr">Exotic Matter</a>.
                    </b-col>
                </b-row>
            </b-container>
        </footer>

        <!-- Pdf viewer popup -->
        <div v-if="docModal" class="doc-view-modal" :class="{open: docModal}">
            <b-container>
                {{ _('Title') }} {{ currentOpenDoc.title }}
            </b-container>
            <b-container>
                <b-row scr>
                    <b-col md="8">
                        <div class="embed-responsive embed-responsive-1by1 doc-pdf ">
                            <iframe v-if="currentOpenDoc.pid" class="embed-responsive-item"
                                    :src="`/assets/pdfjs/web/viewer.html?file=/app/uploads/` + currentOpenDoc.pid">
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
                        <b-button variant="secondary" @click="docModal = false">Close</b-button>
                    </b-col>
                </b-row>
            </b-container>
        </div>

        <b-modal v-if="newFolderModal" v-model="newFolderModal" @ok="createNewFolder"
                 :ok-disabled="newFolderName === ''"
                 :cancel-title="_('Cancel')"
                 :ok-title="_('Create')">
            <span slot="modal-title">{{ _('Create a new folder') }}</span>
            <b-container>
                <!-- TODO add current folder name to title -->
                <b-form-group
                        id="fieldset-new-folder"
                        :description="_('The name of the folder')"
                        :label="_('The folder will be created in the current folder.')"
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

                // Alerts
                showAlert: false,
                alertType: "danger",
                alertMessage: "",

                // Documents list
                docs: [],
                docPid: null,
                docModal: false,
                lastRefresh: Date.now(),

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
            if(ftlAccountElem){
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
            _: function(text) {
                return gettext(text);
            },

            alert: function (message) {
                this.alertMessage = message;
                this.showAlert = true;
            },

            refreshFolders: function () {
                this.updateFolder(this.getCurrentFolder);
            },

            changeFolder: function (folder=null) {
                if (folder) this.previousLevels.push(folder);
                this.updateFolder(folder);
                this.updateDocument();
            },

            changeToPreviousFolder: function () {
                this.previousLevels.pop(); // Remove current level
                let level = this.getCurrentFolder;
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
                    }).catch(error => vi.alert(error));
            },

            updateDocument: function () {
                const vi = this;
                let qs = '';

                if (vi.previousLevels.length > 0) {
                    qs = '?level=' + this.getCurrentFolder.id;
                }

                axios
                    .get('/app/api/v1/documents/' + qs)
                    .then(response => {
                        vi.docs = response.data['results'];
                        vi.lastRefresh = Date.now();
                    }).catch(error => vi.alert(error));
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
                    }).catch(error => vi.alert(error));
            },

            createNewFolder: function () {
                const vi = this;
                let parent = null;

                // Pass CSRF token from cookie to XHR call header (handled by Axios)
                let axiosConfig = {
                    xsrfCookieName: 'csrftoken',
                    xsrfHeaderName: 'X-CSRFToken'
                };

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
                    }).catch(error => vi.alert(error));
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
