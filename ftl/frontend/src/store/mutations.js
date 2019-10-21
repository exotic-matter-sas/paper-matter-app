export default {
  selectMoveTargetFolder: function (state, folder) {
    state.selectedMoveTargetFolder = folder;
  },

  selectPanelFolder: function (state, folder) {
    state.panelSelectedFolder = folder;
  },

  selectDocuments: function (state, documents) {
    for (const document of documents) {
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
  },

  changeSortHome: function (state, value) {
    state.sortHome = value;
  }
}
