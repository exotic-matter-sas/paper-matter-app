/*
 * Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
 * Licensed under the BSL License. See LICENSE in the project root for license information.
 */

export default {
  FTLTreeItemSelected(state) {
    return (itemId) => {
      return (
        state.selectedMoveTargetFolder &&
        state.selectedMoveTargetFolder.id === itemId
      );
    };
  },

  FTLDocumentSelected(state) {
    return (docPid) => {
      return (
        state.selectedDocumentsHome.findIndex((x) => x.pid === docPid) > -1
      );
    };
  },

  getCurrentFolder(state) {
    if (state.previousLevels.length) {
      return state.previousLevels[state.previousLevels.length - 1];
    } else {
      return null;
    }
  },
};
