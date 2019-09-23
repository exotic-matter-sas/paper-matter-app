export default {
  FTLTreeItemSelected(state) {
    return (itemId) => {
      return state.selectedMoveTargetFolder && state.selectedMoveTargetFolder.id === itemId;
    }
  },

  FTLDocumentSelected(state) {
    return (docPid) => {
      return state.selectedDocumentsHome.findIndex(x => x.pid === docPid) > -1;
    }
  }
}
