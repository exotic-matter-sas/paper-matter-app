<template>
    <b-col sm="3" :id="doc.pid" class="document-thumbnail">
        <b-row class="text-truncate document-title"><span @click="$emit('event-open-doc', doc.pid)">{{ doc.title }}</span></b-row>
        <b-row align-h="center">
            <b-img :src="'https://placeimg.com/150/200/arch?' + doc.pid" class="img-thumbnail" slot="aside"
                   width="128" height="200" blank-color="#abc" @click="$emit('event-open-doc', doc.pid)"/>
        </b-row>
        <b-row>
            <small>{{ getDate }}</small>
        </b-row>
        <b-row align-h="center">Note: {{ doc.note }}</b-row>

        <b-row>
            <b-col>
                <b-button variant="secondary" size="sm" :href="'uploads/' + doc.pid">Download here</b-button>
            </b-col>
            <b-col>
                <b-button class="delete-document" variant="danger" size="sm" :disabled="deleting" @click.once="deleteDocument">
                    <b-spinner :class="{'d-none': !deleting}" small></b-spinner>
                    <span :class="{'d-none': deleting}">!! Delete doc (no warn) !!</span>
                </b-button>
            </b-col>
        </b-row>
    </b-col>
</template>

<script>
    import axios from 'axios'

    export default {
        props: {
            doc: {
                type: Object,
                required: true
            }
        },

        data() {
            return {
                deleting: false
            }
        },

        computed: {
            getDate: function () {
                return new Date(this.doc.created);
            }
        },

        methods: {
            deleteDocument: function () {
                let vi = this;
                vi.deleting = true;

                // Pass CSRF token from cookie to XHR call header (handled by Axios)
                let axiosConfig = {
                    xsrfCookieName: 'csrftoken',
                    xsrfHeaderName: 'X-CSRFToken'
                };

                axios
                    .delete('/app/api/v1/documents/' + this.doc.pid, axiosConfig)
                    .then(() => vi.$emit('event-delete-doc'))
                    .catch(error => alert(error));
            }
        }
    }
</script>
