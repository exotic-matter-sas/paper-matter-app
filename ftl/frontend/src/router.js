/*
 * Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
 * Licensed under the Business Source License. See LICENSE in the project root for license information.
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
    // Search page
    {
      path: "/search/:search",
      name: "home-search",
      component: HomeSearch,
      props: (route) => ({
        searchQuery: route.params.search,
        doc: route.query.doc,
      }),
    },
    // Two entries for Home component because /home/:path*/:folderId* entry doesn't work for both cases FIXME
    {
      path: "/folder/*/:folderId(\\d+)",
      name: "home-folder",
      component: Home,
      props: (route) => ({
        doc: route.query.doc,
        folderId: route.params.folderId,
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
