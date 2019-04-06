<template>
    <div id="app" class="m-0">
        <b-container fluid class="p-0">
            <FTLNavbar/>
        </b-container>

        <b-container>
            <b-row>
                <b-col>
                    <FTLUpload @newupload="updateDocument"/>
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
            <ul>
                <FTLFolder v-for="folder in folders" :key="folder.id" :folder="folder"
                           @event-change-folder="changeFolder"/>
            </ul>
        </b-container>

        <b-container>
            <b-row align-h="around" v-if="docs.length">
                <FTLDocument v-for="doc in docs" :key="doc.pid" :doc="doc" @event-delete-doc="updateDocument"/>
            </b-row>
            <b-row v-else>
                <b-col>Aucun document</b-col>
            </b-row>
        </b-container>
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
                folders: [],
                lastRefresh: Date.now()
            }
        },

        mounted() {
            this.changeFolder(0);
        },

        computed: {
            lastRefreshFormatted: function () {
                return new Date(this.lastRefresh);
            }
        },

        methods: {
            changeFolder: function (level) {
                this.updateDocument(level);
                this.updateFolder(level);
            },

            updateDocument: function (level = 0) {
                const vi = this;
                let qs = '';

                if (level > 0) {
                    qs = '?level=' + level;
                }

                axios
                    .get('/app/api/v1/documents/' + qs)
                    .then(response => {
                        vi.docs = response.data['results'];
                        vi.lastRefresh = Date.now();
                    });
            },

            updateFolder: function (level = 0) {
                const vi = this;
                let qs = '';

                if (level > 0) {
                    qs = '?level=' + level;
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
