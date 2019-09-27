import {createLocalVue, shallowMount} from '@vue/test-utils';

import axios from 'axios';
import BootstrapVue from "bootstrap-vue";
import flushPromises from "flush-promises"; // needed for async tests
import * as tv from './../tools/testValues.js'
import {axiosConfig} from "../../src/constants";
import Vuex from 'vuex';

import HomeBase from "../../src/views/HomeBase";
import FTLUpload from "../../src/components/FTLUpload";
import FTLDocument from "../../src/components/FTLDocument";
import storeConfig from "@/store/storeConfig";
import cloneDeep from "lodash.clonedeep";

const localVue = createLocalVue();
localVue.use(BootstrapVue); // to avoid warning on tests execution
localVue.use(Vuex);
localVue.component('font-awesome-icon', jest.fn()); // avoid font awesome warning
localVue.prototype.$_ = (text) => {
  return text;
}; // i18n mock
localVue.prototype.$moment = () => {
  return {fromNow: jest.fn()}
};
localVue.prototype.$router = {push: jest.fn()}; // router mock
const mockedRouteName = jest.fn();
localVue.prototype.$route = {
  get name() {
    return mockedRouteName()
  }
}; // router mock
const mockedMixinAlert = jest.fn();
localVue.mixin({methods: {mixinAlert: mockedMixinAlert}}); // mixin alert

jest.mock('axios', () => ({
  get: jest.fn(),
  post: jest.fn(),
  patch: jest.fn()
}));

jest.mock('../../src/thumbnailGenerator', () => ({
  __esModule: true,
  createThumbFromUrl: jest.fn()
}));

jest.mock('axios', () => ({
  get: jest.fn(),
  post: jest.fn(),
  patch: jest.fn()
}));
const mockedGetFoldersResponse = {
  data: [],
  status: 200,
  config: axiosConfig
};
const mockedGetFolderResponse = {
  data: {
    id: tv.FOLDER_PROPS_VARIANT.id,
    name: tv.FOLDER_PROPS_VARIANT.name,
    paths: [
      tv.FOLDER_PROPS,
    ]
  },
  status: 200
};
const mockedGetDocumentDetailWithThumbResponse = {
  data: tv.DOCUMENT_PROPS,
  status: 200,
  config: axiosConfig
};
const mockedGetDocumentDetailWithoutThumbResponse = {
  data: tv.DOCUMENT_NO_THUMB_PROPS,
  status: 200,
  config: axiosConfig
};
const mockedGetDocumentsResponse = {
  data: {results: []},
  status: 200,
  config: axiosConfig
};

const mockedUpdateFolders = jest.fn();
const mockedChangeFolder = jest.fn();
const mockedOpenDocument = jest.fn();
const mockedRefreshFolders = jest.fn();
const mockedCreateThumbnailForDocument = jest.fn();
const mockedNavigateToFolder = jest.fn();
const mockedComputeFolderUrlPath = jest.fn();
const mockedRefreshDocumentWithSearch = jest.fn();
const mockedUpdateDocuments = jest.fn();
const mockedUpdateFoldersPath = jest.fn();
const mockedNavigateToDocument = jest.fn();
const mockedGetCurrentFolder = jest.fn();
const mockedFolderCreated = jest.fn();
const mockedBreadcrumb = jest.fn();
const mockedDocumentDeleted = jest.fn();
const mockedDocumentUpdated = jest.fn();
const mockedDocumentsSelected = jest.fn();
const mockedDocumentsCreated = jest.fn();

const mountedMocks = {
  updateDocuments: mockedUpdateDocuments,
  refreshFolders: mockedRefreshFolders,
  documentUpdated: mockedDocumentUpdated
};

describe('Home computed', () => {
  let wrapper;
  let storeConfigCopy; // deep copy storeConfig for tests not to pollute it
  let store;
  const fakePath = 'fakeComputeFolderPath';

  beforeEach(() => {
    mockedComputeFolderUrlPath.mockReturnValue(fakePath);
    mockedDocumentsSelected.mockReturnValue([]);
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(storeConfigCopy);
    wrapper = shallowMount(HomeBase, {
      localVue,
      store,
      methods: Object.assign(
        {
          changeFolder: mockedChangeFolder,
          refreshDocumentWithSearch: mockedRefreshDocumentWithSearch,
          computeFolderUrlPath: mockedComputeFolderUrlPath,
        },
        mountedMocks
      ),
      computed: {
        documentsSelected: mockedDocumentsSelected
      }
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });
});

describe('Home mounted call proper methods with given props', () => {
  let storeConfigCopy; // deep copy storeConfig for tests not to pollute it
  let store;
  beforeEach(() => {
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(storeConfigCopy);
    jest.clearAllMocks();
  });

  it('mounted call proper methods with doc props', () => {
    shallowMount(HomeBase, {
      localVue,
      store,
      methods: {
        openDocument: mockedOpenDocument
      },
      computed: {
        documentsSelected: mockedDocumentsSelected
      },
      propsData: {doc: tv.DOCUMENT_PROPS}
    });

    // then
    expect(mockedOpenDocument).toHaveBeenCalledTimes(1);
  });
});

describe('Home watchers call proper methods', () => {
  let wrapper;
  let storeConfigCopy; // deep copy storeConfig for tests not to pollute it
  let store;

  beforeEach(() => {
    mockedDocumentsSelected.mockReturnValue([]);
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(storeConfigCopy);
    wrapper = shallowMount(HomeBase, {
      localVue,
      store,
      methods: Object.assign(
        {
          refreshDocumentWithSearch: mockedRefreshDocumentWithSearch,
          openDocument: mockedOpenDocument,
          changeFolder: mockedChangeFolder,
          updateFoldersPath: mockedUpdateFoldersPath
        },
        mountedMocks
      ),
      computed: {
        documentsSelected: mockedDocumentsSelected
      }
    });
    jest.clearAllMocks();
  });

  it('doc watcher call openDocument if doc value not undefined', () => {
    //when doc is defined
    let doc = tv.DOCUMENT_PROPS.pid;
    wrapper.setData({doc});

    // then
    expect(mockedOpenDocument).toHaveBeenCalledTimes(1);
    expect(mockedOpenDocument).toHaveBeenCalledWith(doc);

    //when doc is reset to undefined
    jest.clearAllMocks();
    doc = undefined;
    wrapper.setData({doc});

    // then
    expect(wrapper.vm.docModal).toBe(false);
    expect(mockedOpenDocument).not.toHaveBeenCalled();
  });

  it('folder watcher call vuex store', async () => {
    // TODO vuex test
  });
});

describe('Home methods call proper methods', () => {
  let wrapper;
  let storeConfigCopy; // deep copy storeConfig for tests not to pollute it
  let store;
  const fakeCurrentFolder = tv.FOLDER_PROPS_WITH_PARENT;
  const fakePath =
    tv.FOLDER_PROPS.name + '/'
    + tv.FOLDER_PROPS_VARIANT.name + '/'
    + tv.FOLDER_PROPS_VARIANT.id;
  beforeEach(() => {
    mockedGetCurrentFolder.mockReturnValue(fakeCurrentFolder);
    mockedComputeFolderUrlPath.mockReturnValue(fakePath);
    mockedDocumentsSelected.mockReturnValue([]);
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(storeConfigCopy);
    wrapper = shallowMount(HomeBase, {
      localVue,
      store,
      methods: Object.assign(
        {
          changeFolder: mockedChangeFolder,
          updateFolders: mockedUpdateFolders,
          createThumbnailForDocument: mockedCreateThumbnailForDocument,
          computeFolderUrlPath: mockedComputeFolderUrlPath,
          refreshDocumentWithSearch: mockedRefreshDocumentWithSearch
        },
        mountedMocks
      ),
      computed: {
        getCurrentFolder: mockedGetCurrentFolder,
        documentsSelected: mockedDocumentsSelected
      }
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('closeDocument call router push', () => {
    // when
    wrapper.vm.closeDocument();

    // then
    expect(wrapper.vm.docPid).toBe(null);
    expect(wrapper.vm.$router.push).toHaveBeenNthCalledWith(1, {path: '/home/' + fakePath});
  });

  it('documentDeleted call updateDocuments when needed', () => {
    wrapper.setData({docs: [tv.DOCUMENT_PROPS, tv.DOCUMENT_PROPS_VARIANT]});
    wrapper.setData({moreDocs: 'moaaarUrl'});

    // when
    wrapper.vm.documentDeleted({doc: tv.DOCUMENT_PROPS_VARIANT});

    // then
    expect(mockedUpdateDocuments).toHaveBeenCalledTimes(0);

    // when
    wrapper.vm.documentDeleted({doc: tv.DOCUMENT_PROPS});

    // then
    expect(mockedUpdateDocuments).toHaveBeenCalledTimes(1);
  });
});

describe('Home methods return proper value', () => {
  let wrapper;
  let storeConfigCopy; // deep copy storeConfig for tests not to pollute it
  let store;

  beforeEach(() => {
    mockedDocumentsSelected.mockReturnValue([]);
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(storeConfigCopy);
    wrapper = shallowMount(HomeBase, {
      localVue,
      store,
      methods: Object.assign(
        {
          changeFolder: mockedChangeFolder,
          updateFolders: mockedUpdateFolders,
          refreshDocumentWithSearch: mockedRefreshDocumentWithSearch,
        },
        mountedMocks
      ),
      computed: {
        documentsSelected: mockedDocumentsSelected
      }
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });
});

describe('Home methods error handling', () => {
  let wrapper;
  let storeConfigCopy; // deep copy storeConfig for tests not to pollute it
  let store;

  beforeEach(() => {
    mockedDocumentsSelected.mockReturnValue([]);
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(storeConfigCopy);
    wrapper = shallowMount(HomeBase, {
      localVue,
      store,
      methods: Object.assign(
        {
          changeFolder: mockedChangeFolder,
          refreshDocumentWithSearch: mockedRefreshDocumentWithSearch,
        },
        mountedMocks
      ),
      computed: {
        documentsSelected: mockedDocumentsSelected
      }
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('updateDocuments call mixinAlert in case of api error', async () => {
    // restore original method to test it
    wrapper.setMethods({_updateDocuments: HomeBase.methods._updateDocuments});
    axios.get.mockRejectedValue('error');
    wrapper.setData({previousLevels: [tv.FOLDER_PROPS, tv.FOLDER_PROPS_VARIANT]});

    // when
    wrapper.vm._updateDocuments();
    await flushPromises(); // wait all pending promises are resolved/rejected

    // then
    expect(mockedMixinAlert).toHaveBeenCalledTimes(1);
  });
});

describe('Home methods call proper api', () => {
  let wrapper;
  let storeConfigCopy; // deep copy storeConfig for tests not to pollute it
  let store;

  beforeEach(() => {
    mockedDocumentsSelected.mockReturnValue([]);
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(storeConfigCopy);
    wrapper = shallowMount(HomeBase, {
        localVue,
        store,
        methods: Object.assign(
          {
            changeFolder: mockedChangeFolder,
            refreshFolders: mockedRefreshFolders,
            createThumbnailForDocument: mockedCreateThumbnailForDocument,
            computeFolderUrlPath: mockedComputeFolderUrlPath,
          },
          mountedMocks
        ),
        computed: {
          breadcrumb: mockedBreadcrumb,
          documentsSelected: mockedDocumentsSelected
        }
      }
    );
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('openDocument call api', () => {
    axios.get.mockResolvedValue(mockedGetDocumentDetailWithoutThumbResponse);
    let opened_document_pid = tv.DOCUMENT_NO_THUMB_PROPS.pid;

    // when
    wrapper.vm.openDocument(opened_document_pid);

    // then
    expect(wrapper.vm.docPid).toBe(opened_document_pid);
  });

  it('updateDocuments call api with sorting older', () => {
    wrapper.setData({sort: 'older'});
    // restore original method to test it
    wrapper.setMethods({updateDocuments: HomeBase.methods.updateDocuments});

    axios.get.mockResolvedValue(mockedGetDocumentsResponse);

    // when
    wrapper.vm._updateDocuments();

    // then
    expect(axios.get).toHaveBeenCalledWith('/app/api/v1/documents?ordering=created');
    expect(axios.get).toHaveBeenCalledTimes(1);
  });

  it('updateDocuments call api with sorting az', () => {
    wrapper.setData({sort: 'az'});
    // restore original method to test it
    wrapper.setMethods({_updateDocuments: HomeBase.methods._updateDocuments});

    axios.get.mockResolvedValue(mockedGetDocumentsResponse);

    // when
    wrapper.vm._updateDocuments();

    // then
    expect(axios.get).toHaveBeenCalledWith('/app/api/v1/documents?ordering=title');
    expect(axios.get).toHaveBeenCalledTimes(1);
  });

  it('updateDocuments call api with sorting za', () => {
    wrapper.setData({sort: 'za'});
    // restore original method to test it
    wrapper.setMethods({_updateDocuments: HomeBase.methods._updateDocuments});

    axios.get.mockResolvedValue(mockedGetDocumentsResponse);

    // when
    wrapper.vm._updateDocuments();

    // then
    expect(axios.get).toHaveBeenCalledWith('/app/api/v1/documents?ordering=-title');
    expect(axios.get).toHaveBeenCalledTimes(1);
  });
});

describe('Home methods update proper data', () => {
  let wrapper;
  let storeConfigCopy; // deep copy storeConfig for tests not to pollute it
  let store;

  beforeEach(() => {
    mockedDocumentsSelected.mockReturnValue([]);
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(storeConfigCopy);
    wrapper = shallowMount(HomeBase, {
      localVue,
      store,
      methods: mountedMocks,
      computed: {
        documentsSelected: mockedDocumentsSelected
      }
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('documentsCreated update docs data', () => {
    let docsList = [tv.DOCUMENT_PROPS];
    //given
    wrapper.setData({docs: docsList});

    // when
    wrapper.vm.documentsCreated({doc: tv.DOCUMENT_PROPS_VARIANT});

    expect(wrapper.vm.docs).toEqual([tv.DOCUMENT_PROPS_VARIANT, tv.DOCUMENT_PROPS]);
  });

  it('documentDeleted update docs data', () => {
    // given
    const documentToDelete = tv.DOCUMENT_NO_THUMB_PROPS_2;
    const originalDocumentsList = [tv.DOCUMENT_NO_THUMB_PROPS, documentToDelete];
    const originalDocumentsListLength = originalDocumentsList.length;
    wrapper.setData({docs: originalDocumentsList});

    // when
    wrapper.vm.documentDeleted({doc: documentToDelete});

    // then
    expect(wrapper.vm.docs.length).toBe(originalDocumentsListLength - 1);
  });

  it('documentUpdated update docs data', () => {
    // given
    wrapper.setMethods({documentUpdated: HomeBase.methods.documentUpdated});
    const documentToUpdate = tv.DOCUMENT_NO_THUMB_PROPS_2;
    const originalDocumentsList = [tv.DOCUMENT_NO_THUMB_PROPS, documentToUpdate];
    const originalDocumentsListLength = originalDocumentsList.length;
    wrapper.setData({docs: originalDocumentsList});

    // when
    const documentUpdated = Object.assign({}, documentToUpdate); // shallow copy
    const updatedTitle = 'bingo!';
    documentUpdated.title = updatedTitle;
    wrapper.vm.documentUpdated({doc: documentUpdated});

    // then
    expect(wrapper.vm.docs.length).toBe(originalDocumentsListLength);
    expect(wrapper.vm.docs[1].title).not.toBe(documentToUpdate.title);
    expect(wrapper.vm.docs[1].title).toBe(updatedTitle);
  });

  it('documentUpdated update currentOpenDoc data if needed', () => {
    // given
    wrapper.setMethods({documentUpdated: HomeBase.methods.documentUpdated});
    const documentToUpdate = tv.DOCUMENT_PROPS;
    const documentNotToUpdate = tv.DOCUMENT_PROPS_VARIANT;
    const originalDocumentsList = [documentNotToUpdate, documentToUpdate];
    wrapper.setData({docs: originalDocumentsList});
    let documentUpdated = Object.assign({}, documentToUpdate); // shallow copy
    documentUpdated.title = 'updated';

    // when no document is open
    wrapper.vm.documentUpdated({doc: documentUpdated});

    // then open doc stay null
    expect(wrapper.vm.currentOpenDoc).toEqual({});

    // when another document is open
    wrapper.setData({currentOpenDoc: documentNotToUpdate});
    wrapper.vm.documentUpdated({doc: documentUpdated});

    // then open doc is not updated
    expect(wrapper.vm.currentOpenDoc).not.toEqual(documentUpdated);

    // when the document to update is open
    wrapper.setData({currentOpenDoc: documentToUpdate});
    wrapper.vm.documentUpdated({doc: documentUpdated});

    // then open doc is updated
    expect(wrapper.vm.currentOpenDoc).toEqual(documentUpdated);
  });

  it('documentDeleted update vuex data', () => {
    // TODO vuex test
  });
});

describe('Home event handling', () => {
  let wrapper;
  let storeConfigCopy; // deep copy storeConfig for tests not to pollute it
  let store;

  beforeEach(() => {
    mockedDocumentsSelected.mockReturnValue([]);
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(storeConfigCopy);
    wrapper = shallowMount(HomeBase, {
      localVue,
      store,
      methods: Object.assign(
        {
          changeFolder: mockedChangeFolder,
          openDocument: mockedOpenDocument,
          navigateToFolder: mockedNavigateToFolder,
          folderCreated: mockedFolderCreated,
          navigateToDocument: mockedNavigateToDocument,
          documentsCreated: mockedDocumentsCreated,
          updateFolders: mockedUpdateFolders,
          documentDeleted: mockedDocumentDeleted,
          documentUpdated: mockedDocumentUpdated
        },
        mountedMocks
      ),
      computed: {
        documentsSelected: mockedDocumentsSelected
      }
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('event-new-upload call updateDocuments', async () => {
    // when
    wrapper.find(FTLUpload).vm.$emit('event-new-upload');
    await flushPromises(); // wait all pending promises are resolved/rejected

    // then
    expect(mockedDocumentsCreated).toHaveBeenCalledTimes(1);
  });

  it('event-open-doc call openDocument', async () => {
    // Need to define at least one document in order FTLDocument component is instantiated
    wrapper.setData({docs: [tv.DOCUMENT_PROPS]});
    let documentPid = tv.DOCUMENT_PROPS.pid;

    // when
    wrapper.find(FTLDocument).vm.$emit('event-open-doc', documentPid);
    await flushPromises(); // wait all pending promises are resolved/rejected

    // then
    expect(mockedNavigateToDocument).toHaveBeenCalledWith(documentPid);
    expect(mockedNavigateToDocument).toHaveBeenCalledTimes(1);
  });

  it('event-delete-doc call documentDeleted', async () => {
    // Need to define at least one document in order FTLDocument component is instantiated
    wrapper.setData({docs: [tv.DOCUMENT_PROPS]});

    // when
    wrapper.find(FTLDocument).vm.$emit('event-delete-doc');
    await flushPromises(); // wait all pending promises are resolved/rejected

    // then
    expect(mockedDocumentDeleted).toHaveBeenCalledTimes(1);
  });
});
