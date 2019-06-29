import Vue from 'vue';
import Router from 'vue-router';
import Home from './views/Home.vue';

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: '/', redirect: '/home'
    },
    {
      path: '/home',
      name: 'home',
      component: Home,
      props: (route) => ({
        searchQuery: route.query.q,
        doc: route.query.doc,
      })
    },
    // Two entries for Home component because /home/:path*/:folder* entry doesn't work for both cases FIXME
    {
      path: '/home/*/:folder(\\d+)',
      name: 'home-folder',
      component: Home,
      props: (route) => ({
        searchQuery: route.query.q,
        doc: route.query.doc,
        paths: route.params.paths,
        folder: route.params.folder
      })
    },
    {
      path: '/konami',
      name: 'konami',
      component: () => import(/* webpackChunkName: "Konami" */ '@/views/Konami.vue'),
    }
  ]
})
