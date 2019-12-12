/*
 * Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
 * Licensed under the BSL License. See LICENSE in the project root for license information.
 */

import {createLocalVue, shallowMount} from '@vue/test-utils';

import axios from 'axios';
import BootstrapVue from "bootstrap-vue";
import flushPromises from "flush-promises"; // needed for async tests
import * as tv from './../tools/testValues.js'
import {axiosConfig} from "../../src/constants";
import Vuex from 'vuex';

import Home from "../../src/views/Home";
import FTLUpload from "../../src/components/FTLUpload";
import FTLFolder from "../../src/components/FTLFolder";
import FTLDocument from "../../src/components/FTLDocument";
import FTLNewFolder from "@/components/FTLNewFolder";
import storeConfig from "@/store/storeConfig";
import cloneDeep from "lodash.clonedeep";
import FTLDocumentPanel from "@/components/FTLDocumentPanel";
import FTLDeleteDocuments from "@/components/FTLDeleteDocuments";
import FTLMoveDocuments from "@/components/FTLMoveDocuments";

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

const mockedUpdateFolders = jest.fn();
const mockedChangeFolder = jest.fn();
const mockedRefreshFolders = jest.fn();
const mockedNavigateToFolder = jest.fn();
const mockedComputeFolderUrlPath = jest.fn();
const mockedRefreshDocumentWithSearch = jest.fn();
const mockedUpdateDocuments = jest.fn();
const mockedUpdateFoldersPath = jest.fn();
const mockedGetCurrentFolder = jest.fn();
const mockedFolderCreated = jest.fn();
const mockedBreadcrumb = jest.fn();
const mockedUnselectAllDocumentsCommit = jest.fn();
const mockedChangeSortHomeCommit = jest.fn();
const mockedDocumentsCreated = jest.fn();
const mockedNavigateToDocument = jest.fn();
const mockedCloseDocument = jest.fn();
const mockedDocumentUpdated = jest.fn();
const mockedDocumentDeleted = jest.fn();

const mountedMocks = {
  updateDocuments: mockedUpdateDocuments,
  refreshFolders: mockedRefreshFolders,
  updateFoldersPath: mockedUpdateFoldersPath,
};

describe('Home template', () => {
  let wrapper;
  let storeConfigCopy;
  let store;
  beforeEach(() => {
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(storeConfigCopy);
    wrapper = shallowMount(Home, {
      localVue,
      store,
      methods: mountedMocks
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('renders properly home template', () => {
    expect(wrapper.text()).toContain('No document yet')
  });
});

describe('Home computed', () => {
  let wrapper;
  let storeConfigCopy; // deep copy storeConfig for tests not to pollute it
  let store;
  const fakePath = 'fakeComputeFolderPath';

  beforeEach(() => {
    mockedComputeFolderUrlPath.mockReturnValue(fakePath);
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(storeConfigCopy);
    wrapper = shallowMount(Home, {
      localVue,
      store,
      methods: Object.assign(
        {
          changeFolder: mockedChangeFolder,
          computeFolderUrlPath: mockedComputeFolderUrlPath,
        },
        mountedMocks
      ),
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('getCurrentFolder return proper format', () => {
    // when
    let getCurrentFolderValue = wrapper.vm.getCurrentFolder;

    // then
    expect(getCurrentFolderValue).toBe(null);

    // when
    wrapper.setData({previousLevels: [tv.FOLDER_PROPS, tv.FOLDER_PROPS_VARIANT]});
    getCurrentFolderValue = wrapper.vm.getCurrentFolder;

    // then
    expect(getCurrentFolderValue).toBe(tv.FOLDER_PROPS_VARIANT);
  });

  it('breadcrumb return proper format', () => {
    const fakeLevels = [tv.FOLDER_PROPS, tv.FOLDER_PROPS_VARIANT];
    wrapper.setData({previousLevels: fakeLevels});

    // when
    const breadcrumbData = wrapper.vm.breadcrumb;

    // then
    const expectedFormat = [
      {
        text: 'Root',
        to: {name: 'home'}
      },
      {
        text: fakeLevels[0].name,
        to: {path: '/home/' + fakePath}
      },
      {
        text: fakeLevels[1].name,
        to: {path: '/home/' + fakePath}
      },
    ];
    expect(breadcrumbData).toEqual(expectedFormat);
    expect(mockedComputeFolderUrlPath).toHaveBeenNthCalledWith(1, fakeLevels[0].id);
    expect(mockedComputeFolderUrlPath).toHaveBeenNthCalledWith(2, fakeLevels[1].id);
    expect(mockedComputeFolderUrlPath).toHaveBeenCalledTimes(2);
  });
});

describe('Home mounted call proper methods with given props and get sort from store', () => {
  let storeConfigCopy; // deep copy storeConfig for tests not to pollute it
  let store;
  const mockedSortValue = 'sortFake';

  beforeEach(() => {
    storeConfigCopy = cloneDeep(storeConfig);
    storeConfigCopy.state.sortHome = mockedSortValue;
    store = new Vuex.Store(storeConfigCopy);
    jest.clearAllMocks();
  });

  it('mounted call proper methods without folders props', async () => {
    const wrapper = shallowMount(Home, {
      localVue,
      store,
      methods: mountedMocks,
    });

    await flushPromises(); // to wait for watchers trigger

    // then
    expect(wrapper.vm.sortHome).toEqual(mockedSortValue);
    expect(mockedRefreshFolders).toHaveBeenCalledTimes(1);
    expect(mockedUpdateDocuments).toHaveBeenCalledTimes(1 + 1); // + 1 for sort watcher
    expect(mockedUpdateFoldersPath).not.toHaveBeenCalled();
  });

  it('mounted call proper methods with folder props', async () => {
    const current_folder = tv.FOLDER_PROPS;

    const wrapper = shallowMount(Home, {
      localVue,
      store,
      methods: mountedMocks,
      propsData: {folder: current_folder}
    });

    await flushPromises(); // to wait for watchers trigger

    // then
    expect(wrapper.vm.sortHome).toEqual(mockedSortValue);
    expect(mockedRefreshFolders).not.toHaveBeenCalled();
    expect(mockedUpdateDocuments).toHaveBeenCalledTimes(1);  // + 1 for sort watcher
    expect(mockedUpdateFoldersPath).toHaveBeenCalledTimes(1);
    expect(mockedUpdateFoldersPath).toHaveBeenCalledWith(current_folder);
  });
});

describe('Home watchers call proper methods', () => {
  let wrapper;
  let storeConfigCopy; // deep copy storeConfig for tests not to pollute it
  let store;

  beforeEach(() => {
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(
      Object.assign( // overwrite some mutations and getter to replace them with mocks
        storeConfigCopy,
        {
          mutations: {
            unselectAllDocuments: mockedUnselectAllDocumentsCommit,
            changeSortHome: mockedChangeSortHomeCommit
          }
        }
      )
    );
    wrapper = shallowMount(Home, {
      localVue,
      store,
      methods: Object.assign(
        {
          changeFolder: mockedChangeFolder,
        },
        mountedMocks
      ),
    });
    jest.clearAllMocks();
  });

  it('folder watcher call proper methods based on route name', async () => {
    const folder = tv.FOLDER_PROPS.id;
    const folderVariant = tv.FOLDER_PROPS_VARIANT.id;
    //when route is home
    mockedRouteName.mockReturnValue('home');
    wrapper.setData({folder});
    await flushPromises();

    // then
    expect(mockedChangeFolder).toHaveBeenCalledTimes(1);
    expect(mockedChangeFolder).toHaveBeenCalledWith();
    expect(mockedUpdateFoldersPath).not.toHaveBeenCalled();

    //when route is home-folder and folder change
    jest.clearAllMocks();
    mockedRouteName.mockReturnValue('home-folder');
    wrapper.setData({folder: folderVariant});

    // then
    expect(mockedChangeFolder).not.toHaveBeenCalled();
    expect(mockedUpdateFoldersPath).toHaveBeenCalledTimes(1);
    expect(mockedUpdateFoldersPath).toHaveBeenCalledWith(folderVariant);
  });

  it('folder watcher commit change to store', async () => {
    const folder = tv.FOLDER_PROPS.id;
    wrapper.setData({folder});
    await flushPromises();

    // then
    expect(mockedUnselectAllDocumentsCommit).toBeCalledTimes(1);
    expect(mockedUnselectAllDocumentsCommit).toBeCalledWith(storeConfigCopy.state, undefined);
  });

  it('sort watcher call updateDocuments', async () => {
    const sort = `fakeSortValue`;
    //when
    wrapper.setData({sort});
    await flushPromises();

    // then
    expect(mockedUpdateDocuments).toHaveBeenCalledTimes(1);
  });

  it('sort watcher commit change to store', async () => {
    const sort = `fakeSortValue`;
    //when
    wrapper.setData({sort});
    await flushPromises();

    // then
    expect(mockedChangeSortHomeCommit).toBeCalledTimes(1);
    expect(mockedChangeSortHomeCommit).toBeCalledWith(storeConfigCopy.state, sort);
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
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(storeConfigCopy);
    wrapper = shallowMount(Home, {
      localVue,
      store,
      methods: Object.assign(
        {
          changeFolder: mockedChangeFolder,
          updateFolders: mockedUpdateFolders,
          computeFolderUrlPath: mockedComputeFolderUrlPath,
        },
        mountedMocks
      ),
      computed: {
        getCurrentFolder: mockedGetCurrentFolder,
      }
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('changeFolder call proper methods', () => {
    // restore original method to test it
    wrapper.setMethods({changeFolder: Home.methods.changeFolder});

    // when
    wrapper.vm.changeFolder(fakeCurrentFolder);

    // then
    expect(mockedUpdateFolders).toHaveBeenCalledTimes(1);
    expect(mockedUpdateFolders).toHaveBeenCalledWith(fakeCurrentFolder);
    expect(mockedUpdateDocuments).toHaveBeenCalledTimes(1);
  });

  it('changeToPreviousFolder call proper methods', async () => {
    const fakePreviousLevels = [tv.FOLDER_PROPS, tv.FOLDER_PROPS_VARIANT];
    wrapper.setData({previousLevels: Array.from(fakePreviousLevels)});

    // when level not null
    wrapper.vm.changeToPreviousFolder();

    // then
    expect(wrapper.vm.previousLevels.length).toBe(fakePreviousLevels.length - 1);
    expect(wrapper.vm.$router.push).toHaveBeenCalledWith({path: '/home/' + fakePath});
    expect(wrapper.vm.$router.push).toHaveBeenCalledTimes(1);
    // TODO try to test the case level === null, seems impossible to do with one beforeEach block since computed cache deactivation is deprecated / doesn't work
  });

  it('refreshFolders call proper methods', () => {
    // restore original method to test it
    wrapper.setMethods({refreshFolders: Home.methods.refreshFolders});

    // when
    wrapper.vm.refreshFolders();

    // then
    expect(mockedUpdateFolders).toHaveBeenCalledTimes(1);
    expect(mockedUpdateFolders).toHaveBeenNthCalledWith(1, fakeCurrentFolder);
  });

  it('refreshAll call proper methods', () => {
    // when
    wrapper.vm.refreshAll();

    // then
    expect(mockedRefreshFolders).toHaveBeenCalledTimes(1);
    expect(mockedUpdateDocuments).toHaveBeenCalledTimes(1);
  });

  it('navigateToFolder call router push', () => {
    const folderToNavigate = tv.FOLDER_PROPS;
    // when
    wrapper.vm.navigateToFolder(folderToNavigate);

    // then
    expect(wrapper.vm.previousLevels[wrapper.vm.previousLevels.length-1]).toEqual(folderToNavigate);
    expect(wrapper.vm.$router.push).toHaveBeenNthCalledWith(1, {path: '/home/' + fakePath});
  });

  it('folderCreated call refreshFolders', () => {
    // when
    wrapper.vm.folderCreated('');

    // then
    expect(mockedRefreshFolders).toHaveBeenCalledTimes(1);
  });
});

describe('Home methods return proper value', () => {
  let wrapper;
  let storeConfigCopy; // deep copy storeConfig for tests not to pollute it
  let store;

  beforeEach(() => {
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(storeConfigCopy);
    wrapper = shallowMount(Home, {
      localVue,
      store,
      methods: Object.assign(
        {
          changeFolder: mockedChangeFolder,
          updateFolders: mockedUpdateFolders,
        },
        mountedMocks
      ),
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('computeFolderUrlPath return proper value', () => {
    // when previousLevels and param id are set
    wrapper.setData({previousLevels: [tv.FOLDER_PROPS, tv.FOLDER_PROPS_VARIANT]});
    let computeFolderUrlPathReturn = wrapper.vm.computeFolderUrlPath(tv.FOLDER_PROPS_VARIANT.id);

    // then
    expect(computeFolderUrlPathReturn).toBe(
      tv.FOLDER_PROPS.name + '/'
      + tv.FOLDER_PROPS_VARIANT.name + '/'
      + tv.FOLDER_PROPS_VARIANT.id
    );

    // when previousLevels and param id not set
    wrapper.setData({previousLevels: [tv.FOLDER_PROPS]});
    computeFolderUrlPathReturn = wrapper.vm.computeFolderUrlPath();

    // then
    expect(computeFolderUrlPathReturn).toBe(
      tv.FOLDER_PROPS.name + '/'
      + tv.FOLDER_PROPS.id
    );

    // when previousLevels empty
    wrapper.setData({previousLevels: []});
    computeFolderUrlPathReturn = wrapper.vm.computeFolderUrlPath();

    // then
    expect(computeFolderUrlPathReturn).toBe('');
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
    wrapper = shallowMount(Home, {
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
});

describe('Home methods call proper api', () => {
  let wrapper;
  let storeConfigCopy; // deep copy storeConfig for tests not to pollute it
  let store;

  beforeEach(() => {
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(storeConfigCopy);
    wrapper = shallowMount(Home, {
        localVue,
        store,
        methods: Object.assign(
          {
            changeFolder: mockedChangeFolder,
            refreshFolders: mockedRefreshFolders,
            computeFolderUrlPath: mockedComputeFolderUrlPath,
          },
          mountedMocks
        ),
        computed: {
          breadcrumb: mockedBreadcrumb,
        }
      }
    );
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('updateFolders call api', () => {
    axios.get.mockResolvedValue(mockedGetFoldersResponse);
    let currentFolder = tv.FOLDER_PROPS_VARIANT;

    // when level param set
    wrapper.vm.updateFolders(currentFolder);

    // then
    expect(axios.get).toHaveBeenCalledWith('/app/api/v1/folders?level=' + currentFolder.id);
    expect(axios.get).toHaveBeenCalledTimes(1);

    // when level param not set
    wrapper.vm.updateFolders();

    // then
    expect(axios.get).toHaveBeenCalledWith('/app/api/v1/folders');
    expect(axios.get).toHaveBeenCalledTimes(2);  });

  it('updateFoldersPath call api', async () => {
    // restore original method to test it
    wrapper.setMethods({updateFoldersPath: Home.methods.updateFoldersPath});

    axios.get.mockResolvedValueOnce(mockedGetFolderResponse);
    wrapper.vm.updateFoldersPath(tv.FOLDER_PROPS.id);
    await flushPromises();

    expect(axios.get).toHaveBeenCalledWith('/app/api/v1/folders/' + tv.FOLDER_PROPS.id);
    expect(axios.get).toHaveBeenCalledTimes(1);
    expect(mockedChangeFolder).toHaveBeenCalledWith(mockedGetFolderResponse.data);
    expect(mockedChangeFolder).toHaveBeenCalledTimes(1);
    expect(mockedComputeFolderUrlPath).toHaveBeenCalledWith(tv.FOLDER_PROPS.id);
    expect(mockedComputeFolderUrlPath).toHaveBeenCalledTimes(1);
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
    wrapper = shallowMount(Home, {
      localVue,
      store,
      methods: mountedMocks,
      computed: {
        documentsSelected: mockedDocumentsSelected
      }
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

});

describe('Home event handling', () => {
  let wrapper;
  let storeConfigCopy; // deep copy storeConfig for tests not to pollute it
  let store;

  beforeEach(() => {
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(Object.assign(
      storeConfigCopy,
      {
        state: {
          selectedDocumentsHome: ['fakeDocument']
        }
      }
    ));
    wrapper = shallowMount(Home, {
      localVue,
      store,
      methods: Object.assign(
        {
          changeFolder: mockedChangeFolder,
          navigateToFolder: mockedNavigateToFolder,
          folderCreated: mockedFolderCreated,
          updateFolders: mockedUpdateFolders,
          documentsCreated: mockedDocumentsCreated,
          navigateToDocument: mockedNavigateToDocument,
          closeDocument: mockedCloseDocument,
          documentUpdated: mockedDocumentUpdated,
          documentDeleted: mockedDocumentDeleted,
        },
        mountedMocks
      ),
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('event-change-folder call navigateToFolder', async () => {
    // Need to define at least one folder in order FTLFolder component is instantiated
    wrapper.setData({folders: [tv.FOLDER_PROPS]});
    let next_folder = tv.FOLDER_PROPS_VARIANT;

    // when
    wrapper.find(FTLFolder).vm.$emit('event-change-folder', next_folder);
    await flushPromises(); // wait all pending promises are resolved/rejected

    // then
    expect(mockedNavigateToFolder).toHaveBeenCalledWith(next_folder);
    expect(mockedNavigateToFolder).toHaveBeenCalledTimes(1);
  });

  it('event-folder-created call folderCreated', async () => {
    // when
    wrapper.find(FTLNewFolder).vm.$emit('event-folder-created');
    await flushPromises(); // wait all pending promises are resolved/rejected

    // then
    expect(mockedFolderCreated).toHaveBeenCalledTimes(1);
  });

 it('event-new-upload call documentsCreated', async () => {
    // when
    wrapper.find(FTLUpload).vm.$emit('event-new-upload');
    await flushPromises(); // wait all pending promises are resolved/rejected

    // then
    expect(mockedDocumentsCreated).toHaveBeenCalledTimes(1);
  });

  it('event-open-doc call navigateToDocument', async () => {
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

  it('event-document-panel-closed call closeDocument', async () => {
    // Need to define docPid in order FTLDocumentPanel component is instantiated
    let documentPid = tv.DOCUMENT_PROPS.pid;
    wrapper.setData({docPid: documentPid});

    // when
    wrapper.find(FTLDocumentPanel).vm.$emit('event-document-panel-closed');
    await flushPromises(); // wait all pending promises are resolved/rejected

    // then
    expect(mockedCloseDocument).toHaveBeenCalledTimes(1);
  });

  it('event-document-renamed call documentUpdated', async () => {
    // Need to define docPid in order FTLDocumentPanel component is instantiated
    let documentPid = tv.DOCUMENT_PROPS.pid;
    wrapper.setData({docPid: documentPid});

    // when
    wrapper.find(FTLDocumentPanel).vm.$emit('event-document-renamed');
    await flushPromises(); // wait all pending promises are resolved/rejected

    // then
    expect(mockedDocumentUpdated).toHaveBeenCalledTimes(1);
  });


  it('event-document-moved on FTLDocumentPanel call documentDeleted', async () => {
    // Need to define docPid in order FTLDocumentPanel component is instantiated
    let documentPid = tv.DOCUMENT_PROPS.pid;
    wrapper.setData({docPid: documentPid});

    // when
    wrapper.find(FTLDocumentPanel).vm.$emit('event-document-moved');
    await flushPromises(); // wait all pending promises are resolved/rejected

    // then
    expect(mockedDocumentDeleted).toHaveBeenCalledTimes(1);
  });

  it('event-document-moved on FTLMoveDocuments call documentDeleted', async () => {
    // Need to define selectedDocumentsHome in beforeEach in order FTLMoveDocuments component is instantiated

    // when
    wrapper.find(FTLMoveDocuments).vm.$emit('event-document-moved');
    await flushPromises(); // wait all pending promises are resolved/rejected

    // then
    expect(mockedDocumentDeleted).toHaveBeenCalledTimes(1);
  });

  it('event-document-deleted call documentDeleted', async () => {
    // Need to define selectedDocumentsHome in beforeEach in order FTLDeleteDocuments component is instantiated

    // when
    wrapper.find(FTLDeleteDocuments).vm.$emit('event-document-deleted');
    await flushPromises(); // wait all pending promises are resolved/rejected

    // then
    expect(mockedDocumentDeleted).toHaveBeenCalledTimes(1);
  });
});
