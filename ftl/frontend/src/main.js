import Vue from 'vue';
import BootstrapVue from 'bootstrap-vue';
import App from './App.vue';

import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-vue/dist/bootstrap-vue.css';
import {mixinAlert} from "./vueMixins";
import router from './router'

Vue.config.productionTip = false;

Vue.use(BootstrapVue);

Vue.prototype.$_ = function (text, vars = null) {
  let translated_text = text;

  if (typeof gettext === 'function') {
    translated_text = gettext(translated_text);
  }

  if (vars !== null) {
    if (typeof interpolate === 'function') {
      if (Array.isArray(vars)) {
        translated_text = interpolate(translated_text, vars);
      } else {
        translated_text = interpolate(translated_text, vars, true);
      }
    }
  }

  return translated_text;
};

// Defined mixins
Vue.mixin({
  methods: {
    mixinAlert
  }
});

new Vue({
  router,
  render: h => h(App)
}).$mount('#app');
