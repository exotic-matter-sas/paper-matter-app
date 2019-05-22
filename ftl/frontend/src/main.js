import Vue from 'vue';
import BootstrapVue from 'bootstrap-vue';
import App from './App.vue';

import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-vue/dist/bootstrap-vue.css';
import {mixinAlert} from "./vueMixins";

Vue.config.productionTip = false;

Vue.use(BootstrapVue);

Vue.prototype.$_ = function (text) {
  var translated_text;
  if (typeof gettext === 'function'){
    translated_text = gettext(text);
  }
  return translated_text || text;
};

// Defined mixins
Vue.mixin({
    methods: {
        mixinAlert
    }
});

new Vue({
    render: h => h(App),
}).$mount('#app');
