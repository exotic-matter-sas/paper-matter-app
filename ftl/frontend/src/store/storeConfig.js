import getters from "@/store/getters";
import mutations from "@/store/mutations";

const state = {
    selectedMoveTargetFolder: null,
    panelSelectedFolder: null,
    selectedDocumentsHome: []
};

export default {
  state,
  getters,
  mutations
}
