/*
 * Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
 * Licensed under the BSL License. See LICENSE in the project root for license information.
 */

import Vue from "vue";
import Router from "vue-router";
import Home from "./views/Home.vue";
import HomeSearch from "@/views/HomeSearch";

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: "/",
      redirect: "/home",
    },
    {
      path: "/home",
      name: "home",
      component: Home,
      props: (route) => ({
        doc: route.query.doc,
        folder: null, // Needed to trigger watched value `folder`
      }),
    },
    // Two entries for Home component because /home/:path*/:folder* entry doesn't work for both cases FIXME
    {
      path: "/home/*/:folder(\\d+)",
      name: "home-folder",
      component: Home,
      props: (route) => ({
        doc: route.query.doc,
        folder: route.params.folder,
      }),
    },
    // Search page
    {
      path: "/home/search/:search",
      name: "home-search",
      component: HomeSearch,
      props: (route) => ({
        searchQuery: route.params.search,
        doc: route.query.doc,
      }),
    },
    {
      path: "/folders/:folder?",
      name: "folders",
      component: () =>
        import(/* webpackChunkName: "folders" */ "./views/ManageFolders.vue"),
      props: true,
    },
    {
      path: "/konami",
      name: "konami",
      component: () =>
        import(/* webpackChunkName: "konami" */ "@/views/Konami.vue"),
    },
  ],
});
