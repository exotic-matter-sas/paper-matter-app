import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    selectedMoveTargetFolder: null,
    panelSelectedFolder: null,
    selectedDocumentsHome: []
  },
  mutations: {
    selectMoveTargetFolder: function (state, folder) {
      state.selectedMoveTargetFolder = folder;
    },

    selectPanelFolder: function (state, folder) {
      state.panelSelectedFolder = folder;
    },

    selectDocuments: function (state, documents) {
      for (const document of documents){
        const foundIndex = state.selectedDocumentsHome.findIndex(x => x.pid === document.pid);
        if (foundIndex === -1) {
          state.selectedDocumentsHome.push(document);
        }
      }
    },

    unselectDocument: function (state, document) {
      const foundIndex = state.selectedDocumentsHome.findIndex(x => x.pid === document.pid);
      if (foundIndex > -1) {
        state.selectedDocumentsHome.splice(foundIndex, 1);
      }
    },

    unselectAllDocuments: function (state) {
      state.selectedDocumentsHome = [];
    }
  },
  actions: {}
})
