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
const mockedPostFolderResponse = {
  data: tv.FOLDER_PROPS,
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

const mockedUpdateFolder = jest.fn();
const mockedChangeFolder = jest.fn();
const mockedOpenDocument = jest.fn();
const mockedAlert = jest.fn();
const mockedRefreshFolder = jest.fn();
const mockedCreateThumbnailForDocument = jest.fn();
const mockedNavigateToFolder = jest.fn();
const mockedComputeFolderUrlPath = jest.fn();
const mockedRefreshDocumentWithSearch = jest.fn();
const mockedUpdateDocuments = jest.fn();

describe('Home script computed', () => {
  let wrapper;

  beforeEach(() => {
    wrapper = shallowMount(Home, {
      localVue,
      methods: {
        changeFolder: mockedChangeFolder,
        refreshFolders: mockedRefreshFolder,
        refreshDocumentWithSearch: mockedRefreshDocumentWithSearch,
        updateDocuments: mockedUpdateDocuments
      } // mock for methods in mount
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
});

describe('Home script methods call proper methods', () => {
  const currentFolder = tv.FOLDER_PROPS;
  let wrapper;

  beforeEach(() => {
    mockedCreateThumbnailForDocument.mockClear();
    wrapper = shallowMount(Home, {
      localVue,
      methods: {
        changeFolder: mockedChangeFolder,
        updateDocuments: mockedUpdateDocuments,
        updateFolders: mockedUpdateFolder,
        createThumbnailForDocument: mockedCreateThumbnailForDocument
      }
    });
  });

  it('mounted call proper methods', () => {
    // view mounted in beforeEach
    // then
    expect(mockedRefreshFolder).toHaveBeenCalled();
    expect(mockedUpdateDocuments).toHaveBeenCalled();
  });

  it('changeFolder call proper methods', () => {
    // override wrapper set in beforeEach as original changeFolder need to be tested here
    wrapper = shallowMount(Home, {
      localVue,
      methods: {
        updateDocuments: mockedUpdateDocuments,
        updateFolders: mockedUpdateFolder,
      }
    });

    // when
    wrapper.vm.changeFolder(currentFolder);

    // then
    expect(mockedUpdateFolder).toHaveBeenCalledWith(currentFolder);
    expect(mockedUpdateDocuments).toHaveBeenCalled();
  });

  it('changeToPreviousFolder call proper methods', () => {
    wrapper.setData({previousLevels: [tv.FOLDER_PROPS, tv.FOLDER_PROPS_VARIANT]});
    let paths = '/home/' + tv.FOLDER_PROPS.name + '/' + tv.FOLDER_PROPS.id;
    // when
    wrapper.vm.changeToPreviousFolder();

    // then
    expect(wrapper.vm.$router.push).toHaveBeenCalledWith({path: paths});
  });

  it('refreshFolders call proper methods', () => {
    wrapper.setData({previousLevels: [tv.FOLDER_PROPS, currentFolder]});

    // when
    wrapper.vm.refreshFolders();

    // then
    expect(mockedUpdateFolder).toHaveBeenCalledWith(currentFolder);
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
    wrapper.vm.navigateToFolder(tv.FOLDER_PROPS);
    const paths = '/home/' + tv.FOLDER_PROPS.name + '/' + tv.FOLDER_PROPS.id;

    expect(wrapper.vm.$router.push).toHaveBeenCalledWith({path: paths});
  });

});

describe('Home script methods return proper value', () => {
  let wrapper;

  beforeEach(() => {
    mockedCreateThumbnailForDocument.mockClear();
    wrapper = shallowMount(Home, {
      localVue,
      methods: {
        changeFolder: mockedChangeFolder,
        updateFolders: mockedUpdateFolder,
        refreshFolders: mockedRefreshFolder,
        refreshDocumentWithSearch: mockedRefreshDocumentWithSearch,
        updateDocuments: mockedUpdateDocuments
      }
    });
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
        refreshFolders: mockedRefreshFolder,
        refreshDocumentWithSearch: mockedRefreshDocumentWithSearch,
      }
    });
  });

  it('updateDocuments call alert method in case of api error', done => {
    axios.get.mockRejectedValue('error');
    let currentFolder = tv.FOLDER_PROPS_VARIANT;
    wrapper.setData({previousLevels: [tv.FOLDER_PROPS, currentFolder]});

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
        methods: {
          changeFolder: mockedChangeFolder,
          refreshFolders: mockedRefreshFolder,
          createThumbnailForDocument: mockedCreateThumbnailForDocument,
          mixinAlert: mockedAlert,
          computeFolderUrlPath: mockedComputeFolderUrlPath
        }
      }
    );
  });

  it('openDocument call api', async () => {
    axios.get.mockResolvedValue(mockedGetDocumentDetailWithoutThumbResponse);
    let opened_document_pid = tv.DOCUMENT_NO_THUMB_PROPS.pid;

    // when
    wrapper.vm.openDocument(opened_document_pid);

    // then
    expect(axios.get).toHaveBeenCalledWith(
      '/app/api/v1/documents/' + opened_document_pid
    );
  });

  it('updateDocuments call api', () => {
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
    // override wrapper set in beforeEach as original createThumbnailForDocument need to be tested here
    wrapper = shallowMount(Home, {
      localVue,
      methods: {
        changeFolder: mockedChangeFolder,
        mixinAlert: mockedAlert,
        updateDocuments: mockedUpdateDocuments
      }
    });
    axios.patch.mockResolvedValue({});

    createThumbFromUrl.mockResolvedValue("base64str");

    wrapper.vm.createThumbnailForDocument(tv.DOCUMENT_PROPS);
    await flushPromises();

    expect(axios.patch).toHaveBeenCalledWith(
      '/app/api/v1/documents/' + tv.DOCUMENT_PROPS.pid,
      {'thumbnail_binary': 'base64str'},
      axiosConfig
    );
  });

  it('updateFoldersPath call api', async () => {
    axios.get.mockResolvedValueOnce(mockedGetFolderResponse);
    wrapper.vm.updateFoldersPath(tv.FOLDER_PROPS.id);
    await flushPromises();

    expect(axios.get).toHaveBeenCalledWith('/app/api/v1/folders/' + tv.FOLDER_PROPS.id);
    expect(mockedChangeFolder).toHaveBeenCalledWith(mockedGetFolderResponse.data);
    expect(mockedComputeFolderUrlPath).toHaveBeenCalledWith(tv.FOLDER_PROPS.id);
  });
});

describe('Home event handling', () => {
  let wrapper;

  beforeEach(() => {
    wrapper = shallowMount(Home, {
      localVue,
      methods: {
        changeFolder: mockedChangeFolder,
        updateDocuments: mockedUpdateDocuments,
        openDocument: mockedOpenDocument,
        navigateToFolder: mockedNavigateToFolder
      }
    });
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
      expect(mockedOpenDocument).toHaveBeenCalledWith(documentPid);
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
});
