import mutations from "@/store/mutations";
import getters from "@/store/getters";
import * as tv from './../tools/testValues.js'

describe('mutations.js', () => {
  it('selectMoveTargetFolder is set', () => {
    const state = { selectedMoveTargetFolder: null };
    const folder = tv.FOLDER_PROPS;
    mutations.selectMoveTargetFolder(state, folder);

    expect(state.selectedMoveTargetFolder).toBe(folder);
  });
  it('selectPanelFolder is set', () => {
    const state = { panelSelectedFolder: null };
    const folder = tv.FOLDER_PROPS;
    mutations.selectPanelFolder(state, folder);

    expect(state.panelSelectedFolder).toBe(folder);
  });
  it('selectDocuments is set with documents not already selected', () => {
    const documentsAlreadySelected = [tv.DOCUMENT_PROPS];
    const documentsNotSelected = [tv.DOCUMENT_PROPS_VARIANT, tv.DOCUMENT_PROPS_WITH_FOLDER];

    const state = { selectedDocumentsHome: documentsAlreadySelected };
    let documentsToSelect = [];
    documentsToSelect = documentsToSelect.concat(documentsAlreadySelected, documentsNotSelected);
    mutations.selectDocuments(state, documentsToSelect);

    expect(state.selectedDocumentsHome).toEqual(documentsToSelect);
  });
  it('unselectDocument unset documents selected', () => {
    const documentAlreadySelected = tv.DOCUMENT_PROPS;
    const documentNotSelected = tv.DOCUMENT_PROPS_VARIANT;

    const state = { selectedDocumentsHome: [documentAlreadySelected] };
    mutations.unselectDocument(state, documentAlreadySelected);

    expect(state.selectedDocumentsHome).toEqual([]);

    mutations.unselectDocument(state, documentNotSelected);

    expect(state.selectedDocumentsHome).toEqual([]);
  });
  it('unselectAllDocuments unset all documents selected', () => {
    const state = { selectedDocumentsHome: [tv.DOCUMENT_PROPS, tv.DOCUMENT_PROPS_VARIANT] };
    mutations.unselectAllDocuments(state);

    expect(state.selectedDocumentsHome).toEqual([]);
  });
});

describe('getters.js', () => {
  it('FTLTreeItemSelected returns proper value', () => {
    const selectedFolder = tv.FOLDER_PROPS;
    const notSelectedFolder = tv.FOLDER_PROPS_VARIANT;
    const state = {selectedMoveTargetFolder: selectedFolder};

    let testedValue = getters.FTLTreeItemSelected(state)(notSelectedFolder.id);

    expect(testedValue).toBe(false);

    testedValue = getters.FTLTreeItemSelected(state)(selectedFolder.id);

    expect(testedValue).toBe(true);
  });

  it('FTLDocumentSelected returns proper value', () => {
    const selectedDocument = tv.DOCUMENT_PROPS;
    const notSelectedDocument = tv.DOCUMENT_PROPS_VARIANT;
    const state = {selectedDocumentsHome: [selectedDocument]};

    let testedValue = getters.FTLDocumentSelected(state)(notSelectedDocument.pid);

    expect(testedValue).toBe(false);

    testedValue = getters.FTLDocumentSelected(state)(selectedDocument.pid);

    expect(testedValue).toBe(true);
  });
});
