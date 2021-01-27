/*
 * Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
 * Licensed under the Business Source License. See LICENSE at project root for more information.
 */

import Vue from "vue";
import {
  BadgePlugin,
  BreadcrumbPlugin,
  ButtonPlugin,
  CalendarPlugin,
  CardPlugin,
  CollapsePlugin,
  FormCheckboxPlugin,
  FormFilePlugin,
  FormGroupPlugin,
  FormInputPlugin,
  FormTextareaPlugin,
  InputGroupPlugin,
  LayoutPlugin,
  LinkPlugin,
  ListGroupPlugin,
  ModalPlugin,
  NavbarPlugin,
  ProgressPlugin,
  SpinnerPlugin,
  TabsPlugin,
  ToastPlugin,
  VBHoverPlugin,
  ButtonGroupPlugin,
} from "bootstrap-vue";
import App from "./App.vue";

import { library } from "@fortawesome/fontawesome-svg-core";
import {
  faArrowRight,
  faArrowLeft,
  faCrown,
  faEdit,
  faExclamationCircle,
  faExternalLinkAlt,
  faFile,
  faFileAlt,
  faFileDownload,
  faFileExcel,
  faFilePdf,
  faFilePowerpoint,
  faFileWord,
  faFolder,
  faFolderOpen,
  faFolderPlus,
  faHome,
  faLevelUpAlt,
  faLink,
  faPen,
  faSearch,
  faShare,
  faSort,
  faSync,
  faTimesCircle,
  faTrash,
  faWindowClose,
  faBell,
} from "@fortawesome/free-solid-svg-icons";
import {
  faMinusSquare,
  faPlusSquare,
  faCalendarAlt,
} from "@fortawesome/free-regular-svg-icons";
import { faMarkdown } from "@fortawesome/free-brands-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";

import { mixinAlert, mixinAlertWarning } from "./vueMixins";
import router from "./router";
import moment from "moment";
import axios from "axios";
import Vuex from "vuex";
import storeConfig from "./store/storeConfig";
import i18n from "./i18n";

Vue.config.productionTip = false;

// Font Awesome icons definition
library.add(
  faHome,
  faFolder,
  faFolderOpen,
  faSearch,
  faWindowClose,
  faTrash,
  faFileDownload,
  faFolderPlus,
  faSync,
  faLevelUpAlt,
  faCrown,
  faEdit,
  faSort,
  faExclamationCircle,
  faMarkdown,
  faExternalLinkAlt,
  faPlusSquare,
  faMinusSquare,
  faFilePdf,
  faFileWord,
  faFileExcel,
  faFile,
  faFilePowerpoint,
  faFileAlt,
  faArrowRight,
  faArrowLeft,
  faTimesCircle,
  faShare,
  faPen,
  faLink,
  faBell,
  faCalendarAlt
);
Vue.component("font-awesome-icon", FontAwesomeIcon);

// Selective use of BootstrapVue for less code bundled
// Vue.use(BootstrapVue);
Vue.use(LayoutPlugin);
Vue.use(FormGroupPlugin);
Vue.use(ModalPlugin);
Vue.use(CardPlugin);
Vue.use(SpinnerPlugin);
Vue.use(ButtonPlugin);
Vue.use(FormCheckboxPlugin);
Vue.use(LinkPlugin);
Vue.use(NavbarPlugin);
Vue.use(CollapsePlugin);
Vue.use(InputGroupPlugin);
Vue.use(FormInputPlugin);
Vue.use(BadgePlugin);
Vue.use(FormTextareaPlugin);
Vue.use(TabsPlugin);
Vue.use(FormFilePlugin);
Vue.use(ProgressPlugin);
Vue.use(ToastPlugin);
Vue.use(BreadcrumbPlugin);
Vue.use(VBHoverPlugin);
Vue.use(CalendarPlugin);
Vue.use(ListGroupPlugin);
Vue.use(ButtonGroupPlugin);

// Moment JS for nice date
Vue.prototype.$moment = moment;
let localeElem = document.getElementById("locale");
if (localeElem) {
  Vue.prototype.$moment.locale(JSON.parse(localeElem.textContent));
}

// Defined mixins
Vue.mixin({
  methods: {
    mixinAlert,
    mixinAlertWarning,
  },
});

// Vuex
Vue.use(Vuex);
const store = new Vuex.Store(storeConfig);

new Vue({
  router,
  store,
  i18n,
  render: (h) => h(App),
}).$mount("#app");

axios.interceptors.response.use(
  function (response) {
    return response;
  },
  function (error) {
    if (error.response.status === 403) {
      // Logout user when an XHR returns 403
      window.location.replace("/logout?auto");
    } else {
      return Promise.reject(error);
    }
  }
);
