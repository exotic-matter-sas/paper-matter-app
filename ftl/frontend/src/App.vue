<template>
    <div id="app">
        <h1>Hello here!</h1>

        <div>
            <button v-on:click="updateDocument">Refresh</button>
            <p>Last refresh {{ lastRefresh }}</p>
        </div>

        <div v-if="docs.length">
            <FTLDocument v-for="doc in docs" v-bind:key="doc.id" v-bind:doc="doc"/>
        </div>
        <p v-else>
            Aucun document
        </p>


    </div>
</template>

<script>
    import FTLDocument from './components/FTLDocument'
    import axios from 'axios'

    export default {
        name: 'app',
        components: {
            FTLDocument
        },

        data() {
            return {
                docs: [], // No doc at start
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
                    .then(response => (this.docs = response.data['results']));
                this.lastRefresh = Date.now()
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
</style>
