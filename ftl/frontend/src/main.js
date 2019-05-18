import Vue from 'vue'
import BootstrapVue from 'bootstrap-vue'
import App from './App.vue'

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

Vue.config.productionTip = false;

Vue.use(BootstrapVue);

// Usage of global mixin https://vuejs.org/v2/guide/mixins.html#Global-Mixin
// Each method should be prefixed with mixin to warn the developer that this method is coming from a mixin
Vue.mixin({
    methods: {
        mixinAlert: function (message, error = false, title = "Notification") {
            this.$bvToast.toast(message, {
                title: title,
                variant: error ? 'danger' : 'success',
                solid: true
            });
        },
    }
});

new Vue({
    render: h => h(App),
}).$mount('#app');
