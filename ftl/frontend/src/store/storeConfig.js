import mutations from "@/store/mutations";
import getters from "@/store/getters";

const state = {
  selectedMoveTargetFolder: null,
  panelSelectedFolder: null,
  selectedDocumentsHome: [],
  sortHome: 'recent'
};

export default {
  state,
  getters,
  mutations
}
