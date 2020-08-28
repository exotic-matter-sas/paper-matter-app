/*
 * Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
 * Licensed under the BSL License. See LICENSE in the project root for license information.
 */

export default {
  appendNewLevel: function (state, folder) {
    state.previousLevels.push(folder);
  },

  removeCurrentLevel: function (state) {
    state.previousLevels.pop();
  },

  setPreviousLevels: function (state, folders) {
    state.previousLevels = folders;
  },

  resetPreviousLevels: function (state) {
    state.previousLevels = [];
  },

  selectMoveTargetFolder: function (state, folder) {
    state.selectedMoveTargetFolder = folder;
  },

  selectPanelFolder: function (state, folder) {
    state.panelSelectedFolder = folder;
  },

  selectDocuments: function (state, documents) {
    for (const document of documents) {
      const foundIndex = state.selectedDocumentsHome.findIndex(
        (x) => x.pid === document.pid
      );
      if (foundIndex === -1) {
        state.selectedDocumentsHome.push(document);
      }
    }
  },

  unselectDocument: function (state, document) {
    const foundIndex = state.selectedDocumentsHome.findIndex(
      (x) => x.pid === document.pid
    );
    if (foundIndex > -1) {
      state.selectedDocumentsHome.splice(foundIndex, 1);
    }
  },

  unselectAllDocuments: function (state) {
    state.selectedDocumentsHome = [];
  },

  changeSortHome: function (state, value) {
    state.sortHome = value;
  },

  setFtlAccount: function (state, value) {
    state.ftlAccount = value;
  },

  setLastOpenedDocument: function (state, value) {
    state.lastOpenedDocument = value;
  },
};
