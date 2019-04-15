<template>
    <transition name="modal">
        <div class="modal-mask">
            <div class="modal-wrapper">
                <div class="modal-container">
                    <b-container fluid>
                        <b-row>Titre {{ docDetail.title }}</b-row>
                        <b-row scr>
                            <pdf :src="'uploads/' + pid"
                                 :page="1">
                                <template slot="loading">
                                    loading content here...
                                </template>
                            </pdf>
                        </b-row>
                        <b-row>
                            <b-button variant="secondary" @click="close">
                                Close
                            </b-button>
                        </b-row>
                    </b-container>
                </div>
            </div>
        </div>
    </transition>
</template>

<script>
    import pdf from 'pdfvuer';
    import axios from 'axios';

    export default {
        name: "FTLViewDocumentPanel",

        components: {
            pdf
        },

        props: {
            pid: {
                type: String,
                required: true
            }
        },

        data() {
            return {
                docDetail: {"title": "Loading"}
            }
        },

        mounted() {
            this.getDocumentDetail(this.pid);
        },

        methods: {
            close: function () {
                this.$emit('event-close-doc');
            },

            getDocumentDetail: function (pid) {
                const vi = this;
                axios
                    .get('/app/api/v1/documents/' + pid)
                    .then(response => {
                        vi.docDetail = response.data;
                    });
            }
        }
    }
</script>

<style scoped>
    .modal-mask {
        position: fixed;
        z-index: 9998;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, .5);
        display: table;
        transition: opacity .3s ease;
    }

    .modal-wrapper {
        display: table-cell;
        vertical-align: middle;
    }

    .modal-container {
        width: 90%;
        height: 90%;
        margin: 0px auto;
        padding: 20px 30px;
        background-color: #fff;
        border-radius: 2px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, .33);
        transition: all .3s ease;
        font-family: Helvetica, Arial, sans-serif;
    }

    .modal-header h3 {
        margin-top: 0;
        color: #42b983;
    }

    .modal-body {
        margin: 20px 0;
    }

    .modal-default-button {
        float: right;
    }

    /*
     * The following styles are auto-applied to elements with
     * transition="modal" when their visibility is toggled
     * by Vue.js.
     *
     * You can easily play with the modal transition by editing
     * these styles.
     */

    .modal-enter {
        opacity: 0;
    }

    .modal-leave-active {
        opacity: 0;
    }

    .modal-enter .modal-container,
    .modal-leave-active .modal-container {
        -webkit-transform: scale(1.1);
        transform: scale(1.1);
    }
</style>