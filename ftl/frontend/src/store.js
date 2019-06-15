import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    selectedFolder: null
  },
  mutations: {
    selectFolder: function (state, folder) {
      state.selectedFolder = folder;
    }
  },
  actions: {}
})
