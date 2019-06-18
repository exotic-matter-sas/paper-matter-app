import Vue from 'vue';
import BootstrapVue from 'bootstrap-vue';
import App from './App.vue';

import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-vue/dist/bootstrap-vue.css';

import {library} from '@fortawesome/fontawesome-svg-core';
import {faFileDownload, faFolder, faHome, faSearch, faTrash, faWindowClose} from '@fortawesome/free-solid-svg-icons';
import {FontAwesomeIcon} from '@fortawesome/vue-fontawesome';

import {mixinAlert} from "./vueMixins";
import router from './router';
import store from './store'

Vue.config.productionTip = false;

// Font Awesome icons definition
library.add(faHome, faFolder, faSearch, faWindowClose, faTrash, faFileDownload);
Vue.component('font-awesome-icon', FontAwesomeIcon);
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
  store,
  render: h => h(App)
}).$mount('#app');
