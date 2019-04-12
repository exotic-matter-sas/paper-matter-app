<template>
    <div id="app" class="m-0">
        <b-container fluid class="p-0">
            <FTLNavbar/>
        </b-container>

        <b-container>
            <b-row>
                <b-col>
                    <FTLUpload :currentFolder="getCurrentFolder" @newupload="updateDocument"/>
                </b-col>
            </b-row>
            <b-row>
                <b-col>
                    <b-button variant="primary" @click="updateDocument">Refresh documents list</b-button>
                    Last refresh {{ lastRefreshFormatted }}
                </b-col>
            </b-row>
        </b-container>

        <b-container>
            <b-row>
                <b-button variant="primary" class="m-1" v-if="previousLevels.length" @click="changeToPreviousFolder">
                    Up
                </b-button>
                <b-button v-else variant="primary" class="m-1" disabled>Up</b-button>
                <FTLFolder v-for="folder in folders" :key="folder.id" :folder="folder"
                           @event-change-folder="changeFolder"/>
            </b-row>
        </b-container>

        <b-container>
            <b-row align-h="around" v-if="docs.length">
                <FTLDocument v-for="doc in docs" :key="doc.pid" :doc="doc" @event-delete-doc="updateDocument"
                             @event-open-doc="openDocument"/>
            </b-row>
            <b-row v-else>
                <b-col>Aucun document</b-col>
            </b-row>
        </b-container>

        <b-container>
            <FTLViewDocumentPanel v-if="docModal" :pid="docPid" @event-close-doc="docModal = false"/>
        </b-container>
    </div>
</template>

<script>
    import FTLNavbar from './components/FTLNavbar'
    import FTLFolder from './components/FTLFolder'
    import FTLDocument from './components/FTLDocument'
    import FTLUpload from './components/FTLUpload'
    import FTLViewDocumentPanel from "./components/FTLViewDocumentPanel"
    import axios from 'axios'

    export default {
        name: 'app',
        components: {
            FTLViewDocumentPanel,
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
                docModal: false
            }
        },

        mounted() {
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
            changeFolder: function (level) {
                if (level) this.previousLevels.push(level);
                this.updateFolder(level);
                this.updateDocument();
            },

            changeToPreviousFolder: function () {
                this.previousLevels.pop(); // Remove current level
                let level = this.previousLevels[this.previousLevels.length - 1]; // Get last
                this.updateFolder(level);
                this.updateDocument();
            },

            openDocument: function (pid) {
                this.docPid = pid;
                this.docModal = true;
            },

            updateDocument: function () {
                const vi = this;
                let qs = '';

                if (vi.previousLevels.length > 0) {
                    qs = '?level=' + vi.previousLevels[vi.previousLevels.length - 1].id;
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

    /* Temp for viewing layout */
    div {
        border: 1px dotted;
    }
</style>
