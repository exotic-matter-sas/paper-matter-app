<template>
    <div :id="doc.pid" class="ftl-document">
        <h1>{{ doc.title}}</h1>
        <small>{{ new Date(doc.created) }}</small>
        <p>Note: {{ doc.note }}</p>
        <a :href="'uploads/' + doc.pid">Download here</a>&nbsp;<a :href="'#' + doc.pid" @click="deleteDocument">!!
        Delete doc (no warn) !!</a>
    </div>
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