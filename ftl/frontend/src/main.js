/*
 * Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
 * Licensed under the BSL License. See LICENSE in the project root for license information.
 */

import Vue from 'vue';
import BootstrapVue from 'bootstrap-vue';
import App from './App.vue';

import {library} from '@fortawesome/fontawesome-svg-core';
import {
  faCrown,
  faEdit,
  faExclamationCircle,
  faFileDownload,
  faFolder,
  faFolderOpen,
  faFolderPlus,
  faHome,
  faLevelUpAlt,
  faSearch,
  faSort,
  faSync,
  faTrash,
  faWindowClose
} from '@fortawesome/free-solid-svg-icons';
import {faMarkdown} from '@fortawesome/free-brands-svg-icons';
import {FontAwesomeIcon} from '@fortawesome/vue-fontawesome';

import {mixinAlert} from "./vueMixins";
import router from './router';
import moment from 'moment'
import axios from 'axios';
import Vuex from 'vuex'
import storeConfig from "./store/storeConfig"
import i18n from './i18n'

Vue.config.productionTip = false;

// Font Awesome icons definition
library.add(faHome, faFolder, faFolderOpen, faSearch, faWindowClose, faTrash, faFileDownload, faFolderPlus, faSync,
  faLevelUpAlt, faCrown, faEdit, faSort, faExclamationCircle, faMarkdown, faExternalLinkAlt);
Vue.component('font-awesome-icon', FontAwesomeIcon);
Vue.use(BootstrapVue);

// Moment JS for nice date
Vue.prototype.$moment = moment;
let localeElem = document.getElementById('locale');
if (localeElem) {
  Vue.prototype.$moment.locale(JSON.parse(localeElem.textContent));
}

// Defined mixins
Vue.mixin({
  methods: {
    mixinAlert
  }
});

// Vuex
Vue.use(Vuex);
const store = new Vuex.Store(storeConfig);

new Vue({
  router,
  store,
  i18n,
  render: h => h(App)
}).$mount('#app');

axios.interceptors.response.use(function (response) {
  return response;
}, function (error) {
  if (error.response.status === 403) {
    // Logout user when an XHR returns 403
    window.location.replace("/logout?auto");
  } else {
    return Promise.reject(error);
  }
});
