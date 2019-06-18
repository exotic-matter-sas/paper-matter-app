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
    // Separated the path because /home/:path*/:folder* doesn't work FIXME
    {
      path: '/home/*/:folder',
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
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (about.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import(/* webpackChunkName: "about" */ './views/About.vue')
    }
  ]
})
