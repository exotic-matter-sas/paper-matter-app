import {createLocalVue, shallowMount} from '@vue/test-utils';

import axios from 'axios';
import BootstrapVue from "bootstrap-vue";

import * as tv from './../tools/testValues.js'
import Home from "../../src/views/Home";
import FTLUpload from "../../src/components/FTLUpload";
import FTLFolder from "../../src/components/FTLFolder";
import FTLDocument from "../../src/components/FTLDocument";
import {axiosConfig} from "../../src/constants";
import flushPromises from "flush-promises";
import {createThumbFromUrl} from '../../src/thumbnailGenerator';
import FTLNewFolder from "@/components/FTLNewFolder";

const localVue = createLocalVue();
localVue.use(BootstrapVue); // to avoid warning on tests execution
localVue.component('font-awesome-icon', jest.fn()); // avoid font awesome warning
localVue.prototype.$_ = (text) => {
  return text;
}; // i18n mock
localVue.prototype.$moment = () => {
  return {fromNow: jest.fn()}
};
localVue.prototype.$router = {push: jest.fn()}; // router mock
localVue.mixin({methods: {mixinAlert: jest.fn()}}); // mixin alert

jest.mock('axios', () => ({
  get: jest.fn(),
  post: jest.fn(),
  patch: jest.fn()
}));

jest.mock('../../src/thumbnailGenerator', () => ({
  __esModule: true,
  createThumbFromUrl: jest.fn()
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
const mockedGetDocumentFlat1Response = {
  data: {
    count: 2,
    next: "http://localhost/next",
    previous: null,
    results: [tv.DOCUMENT_PROPS, tv.DOCUMENT_NO_THUMB_PROPS]
  },
  status: 200,
};
const mockedGetDocumentFlat2Response = {
  data: Promise.resolve({
    count: 1,
    next: null,
    previous: "http://localhost/previous",
    results: [tv.DOCUMENT_NO_THUMB_PROPS_2]
  }),
  status: 200,
};

const mockedUpdateFolders = jest.fn();
const mockedChangeFolder = jest.fn();
const mockedOpenDocument = jest.fn();
const mockedAlert = jest.fn();
const mockedRefreshFolders = jest.fn();
const mockedCreateThumbnailForDocument = jest.fn();
const mockedNavigateToFolder = jest.fn();
const mockedComputeFolderUrlPath = jest.fn();
const mockedRefreshDocumentWithSearch = jest.fn();
const mockedUpdateDocuments = jest.fn();
const mockedUpdateFoldersPath = jest.fn();
const mockedNavigateToDocument = jest.fn();
const mockedGetCurrentFolder =  jest.fn();
const mockedFolderCreated = jest.fn();

const mountedMocks = {
  updateDocuments: mockedUpdateDocuments,
  refreshFolders: mockedRefreshFolders,
};

describe('Home template', () => {
  const wrapper = shallowMount(Home, {
    localVue,
    methods: {
      refreshFolders: mockedRefreshFolders,
      updateDocuments: mockedUpdateDocuments,
    } // mock methods called in mounted
  });

  it('renders properly home template', () => {
    expect(wrapper.text()).toContain('No document yet')
  });
});

describe('Home script computed', () => {
  let wrapper;
  const fakePath = 'fakeComputeFolderPath';

  beforeEach(() => {
    mockedComputeFolderUrlPath.mockReturnValue(fakePath);
    wrapper = shallowMount(Home, {
      localVue,
      methods: {
        // mock for methods in mounted
        changeFolder: mockedChangeFolder,
        refreshFolders: mockedRefreshFolders,
        refreshDocumentWithSearch: mockedRefreshDocumentWithSearch,
        updateDocuments: mockedUpdateDocuments,
        // mock method call in breadcrumb
        computeFolderUrlPath: mockedComputeFolderUrlPath
      }
    });
  });

  it('lastRefreshFormatted return proper format', () => {
    // when
    let lastRefreshFormattedValue = wrapper.vm.lastRefreshFormatted;

    // then
    expect(lastRefreshFormattedValue).toBeInstanceOf(Date);
  });

  it('getCurrentFolder return proper format', () => {
    // when
    wrapper.setData({previousLevels: [tv.FOLDER_PROPS, tv.FOLDER_PROPS_VARIANT]});
    let getCurrentFolderValue = wrapper.vm.getCurrentFolder;

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

  });
});

describe('Mounted call proper methods with given props', () => {

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('mounted call proper methods without props ', () => {
    shallowMount(Home, {
      localVue,
      methods: {
        refreshFolders: mockedRefreshFolders,
        updateDocuments: mockedUpdateDocuments,
      }
    });

    // then
    expect(mockedRefreshFolders).toHaveBeenCalledTimes(1);
    expect(mockedUpdateDocuments).toHaveBeenCalledTimes(1);
    expect(mockedOpenDocument).not.toHaveBeenCalled();
  });

  it('mounted call proper methods with doc props ', () => {
    shallowMount(Home, {
      localVue,
      methods: {
        refreshFolders: mockedRefreshFolders,
        updateDocuments: mockedUpdateDocuments,
        openDocument: mockedOpenDocument
      },
      propsData: {doc: tv.DOCUMENT_PROPS}
    });

    // then
    expect(mockedRefreshFolders).toHaveBeenCalledTimes(1);
    expect(mockedUpdateDocuments).toHaveBeenCalledTimes(1);
    expect(mockedOpenDocument).toHaveBeenCalledTimes(1);
  });

  it('mounted call proper methods with folder props ', () => {
    const current_folder = tv.FOLDER_PROPS;

    shallowMount(Home, {
      localVue,
      methods: {
        refreshFolders: mockedRefreshFolders,
        updateDocuments: mockedUpdateDocuments,
        updateFoldersPath: mockedUpdateFoldersPath
      },
      propsData: {folder: current_folder}
    });

    // then
    expect(mockedRefreshFolders).not.toHaveBeenCalled();
    expect(mockedUpdateDocuments).toHaveBeenCalledTimes(1);
    expect(mockedUpdateFoldersPath).toHaveBeenCalledTimes(1);
    expect(mockedUpdateFoldersPath).toHaveBeenCalledWith(current_folder);
  });

  it('mounted call proper methods with searchQuery props ', () => {
    const search_query = 'coucou!';

    shallowMount(Home, {
      localVue,
      methods: {
        refreshFolders: mockedRefreshFolders,
        updateDocuments: mockedUpdateDocuments,
        refreshDocumentWithSearch: mockedRefreshDocumentWithSearch
      },
      propsData: {searchQuery: search_query}
    });

    // then
    expect(mockedRefreshFolders).toHaveBeenCalledTimes(1);
    expect(mockedUpdateDocuments).not.toHaveBeenCalled();
    expect(mockedRefreshDocumentWithSearch).toHaveBeenCalledTimes(1);
    expect(mockedRefreshDocumentWithSearch).toHaveBeenCalledWith(search_query);
  });
});

describe('Watchers call proper methods', () => {
  let wrapper;

  beforeEach(() => {
    wrapper = shallowMount(Home, {
      localVue,
      methods: {
        refreshFolders: mockedRefreshFolders,
        updateDocuments: mockedUpdateDocuments,
        refreshDocumentWithSearch: mockedRefreshDocumentWithSearch,
        openDocument: mockedOpenDocument,
        changeFolder: mockedChangeFolder,
        updateFoldersPath: mockedUpdateFoldersPath
      }
    });
    jest.clearAllMocks();
  });

  it('searchQuery watcher call refreshDocumentWithSearch', () => {
    // wrapper mounted in beforeEach
    const searchQuery = 'key words';

    //when
    wrapper.setData({searchQuery});

    // then
    expect(mockedRefreshDocumentWithSearch).toHaveBeenCalledTimes(1);
    expect(mockedRefreshDocumentWithSearch).toHaveBeenCalledWith(searchQuery);
  });

  it('doc watcher call openDocument if doc value not undefined', () => {
    // wrapper mounted in beforeEach

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

  it('folder watcher call proper method', () => {
    // wrapper mounted in beforeEach

    //when folder is defined
    let folder = tv.FOLDER_PROPS.id;
    wrapper.setData({folder});

    // then
    expect(mockedChangeFolder).not.toHaveBeenCalled();
    expect(mockedUpdateFoldersPath).toHaveBeenCalledTimes(1);
    expect(mockedUpdateFoldersPath).toHaveBeenCalledWith(folder, true);

    //when folder value is reset to undefined
    jest.clearAllMocks();
    folder = undefined;
    wrapper.setData({folder});

    // then
    expect(mockedChangeFolder).toHaveBeenCalledTimes(1);
    expect(mockedUpdateFoldersPath).not.toHaveBeenCalled();
  });
});

describe('Home script methods call proper methods', () => {
  const fakeCurrentFolder = tv.FOLDER_PROPS_WITH_PARENT;
  const fakePath =
    tv.FOLDER_PROPS.name + '/'
    + tv.FOLDER_PROPS_VARIANT.name + '/'
    + tv.FOLDER_PROPS_VARIANT.id;
  let wrapper;

  beforeEach(() => {
    mockedGetCurrentFolder.mockReturnValue(fakeCurrentFolder);
    mockedComputeFolderUrlPath.mockReturnValue(fakePath);
    wrapper = shallowMount(Home, {
      localVue,
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
        getCurrentFolder: mockedGetCurrentFolder
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

  it('changeToPreviousFolder call proper methods', () => {
    const fakePreviousLevels = [tv.FOLDER_PROPS, tv.FOLDER_PROPS_VARIANT];
    wrapper.setData({previousLevels: Array.from(fakePreviousLevels)});

    // when
    wrapper.vm.changeToPreviousFolder();

    // then
    expect(wrapper.vm.previousLevels.length).toBe(fakePreviousLevels.length - 1);
    expect(wrapper.vm.$router.push).toHaveBeenNthCalledWith(1, {path: '/home/' + fakePath});
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

    // then (called 2 times because there is calls in mounted)
    expect(mockedRefreshFolders).toHaveBeenCalledTimes(1);
    expect(mockedUpdateDocuments).toHaveBeenCalledTimes(1);
  });

  it('generateMissingThumbnail call proper methods', async () => {
    axios.get.mockResolvedValueOnce(mockedGetDocumentFlat1Response);
    axios.get.mockResolvedValueOnce(mockedGetDocumentFlat2Response);

    wrapper.vm.generateMissingThumbnail();
    await flushPromises();

    // Only 2 thumbnails are not available in the 3 documents listed
    expect(mockedCreateThumbnailForDocument).toHaveBeenCalledTimes(2)
  });

  it('openDocument call createThumbnailForDocument if needed', async () => {
    axios.get.mockResolvedValueOnce(mockedGetDocumentDetailWithThumbResponse);
    axios.get.mockResolvedValueOnce(mockedGetDocumentDetailWithoutThumbResponse);

    // when open document is called for a document with thumbnail
    wrapper.vm.openDocument(tv.DOCUMENT_PROPS.pid);
    await flushPromises();

    // then thumbnail generation isn't needed
    expect(mockedCreateThumbnailForDocument).not.toHaveBeenCalled();

    // when open document is called for a document without thumbnail
    wrapper.vm.openDocument(tv.DOCUMENT_NO_THUMB_PROPS.pid);
    await flushPromises();

    // then thumbnail generation is needed
    expect(mockedCreateThumbnailForDocument).toHaveBeenCalledWith(tv.DOCUMENT_NO_THUMB_PROPS);
  });

  it('navigateToFolder call router push', () => {
    // when
    wrapper.vm.navigateToFolder(tv.FOLDER_PROPS);

    // then
    expect(wrapper.vm.$router.push).toHaveBeenNthCalledWith(1, {path: '/home/' + fakePath});
  });

  it('closeDocument call router push', () => {
    // when
    wrapper.vm.navigateToFolder(tv.FOLDER_PROPS);

    // then
    expect(wrapper.vm.$router.push).toHaveBeenNthCalledWith(1, {path: '/home/' + fakePath});
  });

  it('refreshDocumentWithSearch call updateDocuments and set currentSearch', () => {
    // restore original method to test it
    wrapper.setMethods({refreshDocumentWithSearch: Home.methods.refreshDocumentWithSearch});

    // when
    const searchQuery = 'coucou !';
    wrapper.vm.refreshDocumentWithSearch(searchQuery);

    // then
    expect(wrapper.vm.currentSearch).toBe(searchQuery);
    expect(mockedUpdateDocuments).toHaveBeenCalledTimes(1);
  });

  it('clearSearch call refreshDocumentWithSearch', () => {
    // when
    wrapper.vm.clearSearch();

    // then
    expect(mockedRefreshDocumentWithSearch).toHaveBeenCalledTimes(1);
    expect(mockedRefreshDocumentWithSearch).toHaveBeenCalledWith('');
  });

  it('folderCreated call refreshFolders', () => {
    // when
    wrapper.vm.folderCreated('');

    // then
    expect(mockedRefreshFolders).toHaveBeenCalledTimes(1);
  });
});

describe('Home script methods return proper value', () => {
  let wrapper;

  beforeEach(() => {
    wrapper = shallowMount(Home, {
      localVue,
      methods: {
        changeFolder: mockedChangeFolder,
        updateFolders: mockedUpdateFolders,
        refreshFolders: mockedRefreshFolders,
        refreshDocumentWithSearch: mockedRefreshDocumentWithSearch,
        updateDocuments: mockedUpdateDocuments
      }
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('computeFolderUrlPath return proper value', () => {
    wrapper.setData({previousLevels: [tv.FOLDER_PROPS, tv.FOLDER_PROPS_VARIANT]});

    let computeFolderUrlPath = wrapper.vm.computeFolderUrlPath(tv.FOLDER_PROPS_VARIANT.id);

    expect(computeFolderUrlPath).toBe(
      tv.FOLDER_PROPS.name
      + '/'
      + tv.FOLDER_PROPS_VARIANT.name
      + '/'
      + tv.FOLDER_PROPS_VARIANT.id);
  });
});

describe('Home script methods error handling', () => {
  let wrapper;

  beforeEach(() => {
    axios.get.mockResolvedValue(mockedGetDocumentsResponse);

    wrapper = shallowMount(Home, {
      localVue,
      methods: {
        changeFolder: mockedChangeFolder,
        mixinAlert: mockedAlert,
        refreshFolders: mockedRefreshFolders,
        refreshDocumentWithSearch: mockedRefreshDocumentWithSearch,
      }
    });
  });

  it('updateDocuments call alert method in case of api error', done => {
    axios.get.mockRejectedValue('error');
    wrapper.setData({previousLevels: [tv.FOLDER_PROPS, tv.FOLDER_PROPS_VARIANT]});

    // when
    wrapper.vm.updateDocuments();

    // then
    wrapper.vm.$nextTick(() => {
      axios.get().catch(() => {
        expect(mockedAlert).toHaveBeenCalled();
        done();
      });
    });
  });
});

describe('Home script methods call proper api', () => {
  let wrapper;

  beforeEach(() => {
    wrapper = shallowMount(Home, {
        localVue,
        methods: Object.assign(
          {
          changeFolder: mockedChangeFolder,
          refreshFolders: mockedRefreshFolders,
          createThumbnailForDocument: mockedCreateThumbnailForDocument,
          mixinAlert: mockedAlert,
          computeFolderUrlPath: mockedComputeFolderUrlPath
          },
          mountedMocks
        ),
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
    expect(axios.get).toHaveBeenNthCalledWith(
      1,
      '/app/api/v1/documents/' + opened_document_pid
    );
  });

  it('updateDocuments call api', () => {
    // restore original method to test it
    wrapper.setMethods({updateDocuments: Home.methods.updateDocuments});

    axios.get.mockResolvedValue(mockedGetDocumentsResponse);
    let currentFolder = tv.FOLDER_PROPS_VARIANT;
    wrapper.setData({previousLevels: [tv.FOLDER_PROPS, currentFolder]});

    // when
    wrapper.vm.updateDocuments();

    // then
    expect(axios.get).toHaveBeenCalledWith(
      '/app/api/v1/documents/?level=' + currentFolder.id
    );
  });

  it('updateFolders call api', () => {
    axios.get.mockResolvedValue(mockedGetFoldersResponse);
    let currentFolder = tv.FOLDER_PROPS_VARIANT;

    // when
    wrapper.vm.updateFolders(currentFolder);

    // then
    expect(axios.get).toHaveBeenCalledWith(
      '/app/api/v1/folders/?level=' + currentFolder.id
    );
  });

  it('generateMissingThumbnail call api', async () => {
    axios.get.mockResolvedValueOnce(mockedGetDocumentFlat1Response);
    axios.get.mockResolvedValueOnce(mockedGetDocumentFlat2Response);

    wrapper.vm.generateMissingThumbnail();
    await flushPromises();

    expect(axios.get).toHaveBeenCalledWith("/app/api/v1/documents?flat=true");
    expect(axios.get).toHaveBeenCalledWith("http://localhost/next");
  });

  it('createThumbnailForDocument call api', async () => {
    // restore original method to test it
    wrapper.setMethods({createThumbnailForDocument: Home.methods.createThumbnailForDocument});
    axios.patch.mockResolvedValue({});

    createThumbFromUrl.mockResolvedValue("base64str");

    wrapper.vm.createThumbnailForDocument(tv.DOCUMENT_PROPS);
    await flushPromises();

    expect(axios.patch).toHaveBeenNthCalledWith(
      1,
      '/app/api/v1/documents/' + tv.DOCUMENT_PROPS.pid,
      {'thumbnail_binary': 'base64str'},
      axiosConfig
    );
  });

  it('updateFoldersPath call api', async () => {
    axios.get.mockResolvedValueOnce(mockedGetFolderResponse);
    wrapper.vm.updateFoldersPath(tv.FOLDER_PROPS.id);
    await flushPromises();

    expect(axios.get).toHaveBeenNthCalledWith(1, '/app/api/v1/folders/' + tv.FOLDER_PROPS.id);
    expect(mockedChangeFolder).toHaveBeenNthCalledWith(1, mockedGetFolderResponse.data);
    expect(mockedComputeFolderUrlPath).toHaveBeenNthCalledWith(1, tv.FOLDER_PROPS.id);
  });
});

describe('Home event handling', () => {
  let wrapper;

  beforeEach(() => {
    wrapper = shallowMount(Home, {
      localVue,
      methods: Object.assign(
        {
        changeFolder: mockedChangeFolder,
        openDocument: mockedOpenDocument,
        navigateToFolder: mockedNavigateToFolder,
        folderCreated: mockedFolderCreated,
        navigateToDocument: mockedNavigateToDocument,
        updateFolders: mockedUpdateFolder
        },
        mountedMocks
      )
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('event-new-upload call updateDocuments', done => {
    // when
    wrapper.find(FTLUpload).vm.$emit('event-new-upload');

    // then
    wrapper.vm.$nextTick(() => {
      expect(mockedUpdateDocuments).toHaveBeenCalled();
      done();
    });
  });

  it('event-change-folder call navigateToFolder', done => {
    // Need to define at least one folder in order FTLFolder component is instantiated
    wrapper.setData({folders: [tv.FOLDER_PROPS]});
    let next_folder = tv.FOLDER_PROPS_VARIANT;

    // when
    wrapper.find(FTLFolder).vm.$emit('event-change-folder', next_folder);

    // then
    wrapper.vm.$nextTick(() => {
      expect(mockedNavigateToFolder).toHaveBeenCalledWith(next_folder);
      done();
    });
  });

  it('event-open-doc call openDocument', done => {
    // Need to define at least one document in order FTLDocument component is instantiated
    wrapper.setData({docs: [tv.DOCUMENT_PROPS]});
    let documentPid = tv.DOCUMENT_PROPS.pid;

    // when
    wrapper.find(FTLDocument).vm.$emit('event-open-doc', documentPid);

    // then
    wrapper.vm.$nextTick(() => {
      expect(mockedNavigateToDocument).toHaveBeenCalledWith(documentPid);
      done();
    });
  });

  it('event-delete-doc call updateDocuments', done => {
    // Need to define at least one document in order FTLDocument component is instantiated
    wrapper.setData({docs: [tv.DOCUMENT_PROPS]});

    // when
    wrapper.find(FTLDocument).vm.$emit('event-delete-doc');

    // then
    wrapper.vm.$nextTick(() => {
      expect(mockedUpdateDocuments).toHaveBeenCalled();
      done();
    });
  });

  it('event-folder-created call folderCreated', done => {
    // when
    wrapper.find(FTLNewFolder).vm.$emit('event-folder-created');

    // then
    wrapper.vm.$nextTick(() => {
      expect(mockedFolderCreated).toHaveBeenCalledTimes(1);
      done();
    });
  });
});
