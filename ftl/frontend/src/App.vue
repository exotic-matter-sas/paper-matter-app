<template>
    <div id="app" class="m-0">
        <header>
            <b-container fluid class="p-0">
                <FTLNavbar :account="account"/>
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
                        <b-button variant="primary" @click="updateDocument">Refresh documents list</b-button>
                        Last refresh {{ lastRefreshFormatted }}
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
                    <b-col>Aucun document</b-col>
                </b-row>
            </b-container>
        </section>

        <footer>
            <b-container>
                <b-row>
                    <b-col>
                        ftl-app, open source software. Made with ❤ by <a href="https://www.exotic-matter.fr">Exotic
                        Matter</a>.
                    </b-col>
                </b-row>
            </b-container>
        </footer>

        <!-- Pdf viewer popup -->
        <div v-if="docModal" class="doc-view-modal" :class="{open: docModal}">
            <b-container>
                Titre {{ currentOpenDoc.title }}
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
                docs: [],
                docPid: null,
                folders: [],
                previousLevels: [],
                lastRefresh: Date.now(),
                docModal: false,
                account: {},
                currentOpenDoc: {title: 'loading'},
                publicPath: process.env.BASE_URL,
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
                    return {};
                }
            }
        },

        methods: {
            changeFolder: function (folder = null) {
                if (folder) this.previousLevels.push(folder);
                this.updateFolder(folder);
                this.updateDocument();
            },

            changeToPreviousFolder: function () {
                this.previousLevels.pop(); // Remove current level
                let level = this.getCurrentFolder;
                this.updateFolder(level);
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
                    });
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
