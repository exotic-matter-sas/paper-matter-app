<template>
    <div id="app">
        <h1>Hello here!</h1>

        <FTLUpload @newupload="updateDocument"/>

        <div>
            <button @click="updateDocument">Refresh documents list</button>
            Last refresh {{ new Date(lastRefresh) }}
        </div>

        <div id="documents" v-if="docs.length">
            <FTLDocument v-for="doc in docs" :key="doc.pid" :doc="doc" @event-delete-doc="updateDocument"/>
        </div>
        <p v-else>
            Aucun document
        </p>
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

    div {
        border: 1px solid;
    }
</style>
