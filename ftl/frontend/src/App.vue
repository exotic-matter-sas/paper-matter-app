<template>
    <div id="app">
        <b-container>
            <b-row>
                <b-col><h1>Hello here!</h1></b-col>
            </b-row>
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
    import FTLDocument from './components/FTLDocument'
    import FTLUpload from './components/FTLUpload'
    import axios from 'axios'

    export default {
        name: 'app',
        components: {
            FTLDocument,
            FTLUpload
        },

        data() {
            return {
                docs: [],
                lastRefresh: Date.now()
            }
        },

        mounted() {
            this.updateDocument()
        },

        computed: {
            lastRefreshFormatted: function () {
                return new Date(this.lastRefresh);
            }
        },

        methods: {
            updateDocument: function () {
                axios
                    .get('/app/api/v1/documents/')
                    .then(response => {
                        this.docs = response.data['results'];
                        this.lastRefresh = Date.now();
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
