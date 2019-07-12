import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    selectedMoveTargetFolder: null,
    panelSelectedFolder: null
  },
  mutations: {
    selectMoveTargetFolder: function (state, folder) {
      state.selectedMoveTargetFolder = folder;
    },

    selectPanelFolder: function (state, folder) {
      state.panelSelectedFolder = folder;
    }
  },
  actions: {}
})
