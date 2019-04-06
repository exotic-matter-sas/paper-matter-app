<template>
    <b-col sm="3" :id="doc.pid">
        <b-row class="text-truncate">{{ doc.title }}</b-row>
        <b-row align-h="center">
            <b-img :src="'https://loremflickr.com/150/200/cats?' + doc.pid" class="img-thumbnail" slot="aside"
                   width="128"
                   blank-color="#abc"/>
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
                <b-button variant="danger" size="sm" :disabled="deleting" @click.once="deleteDocument">
                    <b-spinner :hidden="!deleting" small></b-spinner>
                    <span :class="{'sr-only': deleting}">!! Delete doc (no warn) !!</span>
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
                    .then(response => {
                        vi.$emit('event-delete-doc', response)
                    })
                    .catch(error => alert(error));
            }
        }
    }
</script>