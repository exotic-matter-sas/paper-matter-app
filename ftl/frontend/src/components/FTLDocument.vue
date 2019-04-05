<template>
    <div id="doc.id" class="ftl-document">
        <h1>{{ doc.title}}</h1>
        <p>{{ doc.note }}</p>
    </div>
</template>

<script>
    export default {
        props: {
            doc: {
                type: Object,
                required: true
            }
        }
    }
</script>