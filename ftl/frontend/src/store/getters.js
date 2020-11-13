/*
 * Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
 * Licensed under the Business Source License. See LICENSE at project root for more information.
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
