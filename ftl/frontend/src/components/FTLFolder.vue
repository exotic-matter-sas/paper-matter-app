<template>
    <b-button class="folder m-1" @click="$emit('event-change-folder', folder)">{{ folder.name }}</b-button>
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
