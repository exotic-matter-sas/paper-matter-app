<template>
    <b-col sm="3" :id="doc.pid">
        <p>{{ doc.title}}</p>
        <small>{{ new Date(doc.created) }}</small>
        <p>Note: {{ doc.note }}</p>
        <b-button variant="secondary" size="sm" :href="'uploads/' + doc.pid">Download here</b-button>
        <b-button variant="danger" size="sm" @click="deleteDocument">!! Delete doc (no warn) !!</b-button>
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

        methods: {
            deleteDocument: function () {
                let vi = this;

                // Pass CSRF token from cookie to XHR call header (handled by Axios)
                let axiosConfig = {
                    xsrfCookieName: 'csrftoken',
                    xsrfHeaderName: 'X-CSRFToken'
                };

                axios
                    .delete('/app/api/v1/documents/' + this.doc.pid, axiosConfig)
                    .then(response => {
                        vi.$emit('event-delete-doc', response)
                    })
                    .catch(error => alert(error));
            }
        }
    }
</script>