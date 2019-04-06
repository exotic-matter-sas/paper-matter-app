<template>
    <li>
        <b-button @click="$emit('event-change-folder', folder.id)">{{ folder.name }}</b-button>
    </li>
</template>

<script>
    export default {
        name: "FTLFolder",

        props: {
            folder: {
                type: Object,
                required: true
            }
        }
    }
</script>

<style scoped>

</style>