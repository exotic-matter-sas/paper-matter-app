/*
 * Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
 * Licensed under the Business Source License. See LICENSE at project root for more information.
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
        folderId: null, // Needed to trigger watched value `folderId`
      }),
    },
    // Two entries for Home component because /home/:path*/:folderId* entry doesn't work for both cases FIXME
    {
      path: "/home/*/:folderId(\\d+)",
      name: "home-folder",
      component: Home,
      props: (route) => ({
        doc: route.query.doc,
        folderId: route.params.folderId,
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
      path: "/konami",
      name: "konami",
      component: () =>
        import(/* webpackChunkName: "konami" */ "@/views/Konami.vue"),
    },
  ],
});
