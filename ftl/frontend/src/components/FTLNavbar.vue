<template>
    <b-navbar toggleable="lg" type="dark" variant="dark">
        <b-navbar-brand href="/app">FTL-APP</b-navbar-brand>

        <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

        <b-collapse id="nav-collapse" is-nav>
            <!-- <b-navbar-nav>
                <b-nav-item href="#">Link</b-nav-item>
                <b-nav-item href="#" disabled>Disabled</b-nav-item>
            </b-navbar-nav> -->

            <!-- Right aligned nav items -->
            <b-navbar-nav class="ml-auto">
                <b-nav-form>
                    <b-form-input id="search-input" size="sm" class="m-1" variant="secondary" placeholder="Search" v-model="search"
                                  @keydown.enter.prevent="$emit('event-search', $event.target.value)"></b-form-input>
                    <b-button id="search-button" size="sm" class="m-1" variant="secondary" type="button" @click="$emit('event-search', search)">
                        {{this.$_('Search')}}
                    </b-button>
                    <b-button size="sm" class="m-1" type="button" variant="secondary"
                              @click="clear">
                        {{this.$_('X')}}
                    </b-button>

                </b-nav-form>

                <b-nav-item-dropdown :text="this.$_('Lang')" right>
                    <b-dropdown-item href="#">EN</b-dropdown-item>
                    <b-dropdown-item href="#">ES</b-dropdown-item>
                    <b-dropdown-item href="#">RU</b-dropdown-item>
                    <b-dropdown-item href="#">FR</b-dropdown-item>
                </b-nav-item-dropdown>

                <b-nav-item-dropdown right>
                    <!-- Using 'button-content' slot -->
                    <template slot="button-content"><em id="username">{{ account.name }}</em></template>
                    <b-dropdown-item href="/account">{{this.$_('Profile')}}</b-dropdown-item>
                    <b-dropdown-item href="/logout">{{this.$_('Sign Out')}}</b-dropdown-item>
                </b-nav-item-dropdown>
            </b-navbar-nav>
        </b-collapse>
    </b-navbar>
</template>

<script>
    export default {
        name: "FTLNavbar",

        props: {
            account: {
                type: Object,
                required: true
            },
        },

        data() {
            return {
                search: ""
            }
        },

        methods: {
            clear: function () {
                this.search = "";
                this.$emit('event-clear-search');
            }
        }
    }
</script>

<style scoped>

</style>
