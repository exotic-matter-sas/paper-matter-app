import {createLocalVue, shallowMount} from '@vue/test-utils';

import axios from 'axios';
import BootstrapVue from "bootstrap-vue";

import * as tv from './../tools/testValues.js'
import App from "../../src/App";
import FTLUpload from "../../src/components/FTLUpload";
import FTLFolder from "../../src/components/FTLFolder";
import FTLDocument from "../../src/components/FTLDocument";
import {axiosConfig} from "../../src/constants";
import flushPromises from "flush-promises";
import {createThumbFromUrl} from '../../src/thumbnailGenerator';

const localVue = createLocalVue();
localVue.use(BootstrapVue); // to avoid warning on tests execution
localVue.prototype.$_ = (text) => {
  return text;
}; // i18n mock
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
const mockedGetDocumentsResponse = {
  data: {results: []},
  status: 200,
  config: axiosConfig
};
const mockedGetDocumentResponse = {
  data: tv.DOCUMENT_PROPS,
  status: 200,
  config: axiosConfig
};
const mockedPostFolderResponse = {
  data: tv.FOLDER_PROPS,
  status: 200,
  config: axiosConfig
};

const mockedUpdateFolder = jest.fn();
const mockedUpdateDocument = jest.fn();
const mockedChangeFolder = jest.fn();
const mockedOpenDocument = jest.fn();
const mockedAlert = jest.fn();
const mockedRefreshFolder = jest.fn();
const mockedCreateThumbnailForDocument = jest.fn();

describe('App template', () => {
  const wrapper = shallowMount(App, {
    localVue,
    methods: {changeFolder: mockedChangeFolder} // mock changeFolder as it is called by mounted
  });

  it('renders properly app template', () => {
    expect(wrapper.text()).toContain('Made with ❤ by', 'Exotic Matter')
  });
});

describe('App script computed', () => {
  let wrapper;

  beforeEach(() => {
    wrapper = shallowMount(App, {
      localVue,
      methods: {changeFolder: mockedChangeFolder} // mock changeFolder as it is called by mounted
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

describe('App script methods call proper methods', () => {
  const currentFolder = tv.FOLDER_PROPS;
  let wrapper;

  beforeEach(() => {
    wrapper = shallowMount(App, {
      localVue,
      methods: {
        changeFolder: mockedChangeFolder,
        updateDocument: mockedUpdateDocument,
        updateFolder: mockedUpdateFolder,
      }
    });
  });

  it('mounted call proper methods', () => {
    // view mounted in beforeEach
    // then
    expect(mockedChangeFolder).toHaveBeenCalled();
  });

  it('changeFolder call proper methods', () => {
    // override wrapper set in beforeEach as original changeFolder need to be tested here
    wrapper = shallowMount(App, {
      localVue,
      methods: {
        updateDocument: mockedUpdateDocument,
        updateFolder: mockedUpdateFolder,
      }
    });

    // when
    wrapper.vm.changeFolder(currentFolder);

    // then
    expect(mockedUpdateFolder).toHaveBeenCalledWith(currentFolder);
    expect(mockedUpdateDocument).toHaveBeenCalled();
  });

  it('changeToPreviousFolder call proper methods', () => {
    let previousFolder = tv.FOLDER_PROPS;
    wrapper.setData({previousLevels: [previousFolder, tv.FOLDER_PROPS_VARIANT]});

    // when
    wrapper.vm.changeToPreviousFolder();

    // then
    expect(mockedUpdateFolder).toHaveBeenCalledWith(previousFolder);
    expect(mockedUpdateDocument).toHaveBeenCalled();
  });

  it('refreshFolders call proper methods', () => {
    wrapper.setData({previousLevels: [tv.FOLDER_PROPS, currentFolder]});

    // when
    wrapper.vm.refreshFolders();

    // then
    expect(mockedUpdateFolder).toHaveBeenCalledWith(currentFolder);
  });
});

describe('App script methods error handling', () => {
  let wrapper;

  beforeEach(() => {
    wrapper = shallowMount(App, {
      localVue,
      methods: {
        changeFolder: mockedChangeFolder,
        mixinAlert: mockedAlert,
      }
    });
  });

  it('updateDocument call alert method in case of api error', done => {
    axios.get.mockRejectedValue('error');
    let currentFolder = tv.FOLDER_PROPS_VARIANT;
    wrapper.setData({previousLevels: [tv.FOLDER_PROPS, currentFolder]});

    // when
    wrapper.vm.updateDocument();

    // then
    wrapper.vm.$nextTick(() => {
      axios.get().catch(() => {
        expect(mockedAlert).toHaveBeenCalled();
        done();
      });
    });
  });
});

describe('App script methods call proper api', () => {
  let wrapper;

  beforeEach(() => {
    axios.get.mockResolvedValueOnce(mockedGetFoldersResponse);
    axios.get.mockResolvedValueOnce(mockedGetDocumentsResponse);
    wrapper = shallowMount(App, {
        localVue,
        methods: {
          refreshFolders: mockedRefreshFolder,
          createThumbnailForDocument: mockedCreateThumbnailForDocument
        }
      }
    );
  });

  it('openDocument call api', async () => {
    axios.get.mockResolvedValue({
      data: tv.DOCUMENT_NO_THUMB_PROPS,
      status: 200,
      config: axiosConfig
    });
    let opened_document_pid = tv.DOCUMENT_NO_THUMB_PROPS.pid;

    // when
    wrapper.vm.openDocument(opened_document_pid);

    // then
    expect(axios.get).toHaveBeenCalledWith(
      '/app/api/v1/documents/' + opened_document_pid
    );
    await flushPromises();
    expect(mockedCreateThumbnailForDocument).toHaveBeenCalledWith(tv.DOCUMENT_NO_THUMB_PROPS);
  });

  it('updateDocument call api', () => {
    axios.get.mockResolvedValue(mockedGetDocumentsResponse);
    let currentFolder = tv.FOLDER_PROPS_VARIANT;
    wrapper.setData({previousLevels: [tv.FOLDER_PROPS, currentFolder]});

    // when
    wrapper.vm.updateDocument();

    // then
    expect(axios.get).toHaveBeenCalledWith(
      '/app/api/v1/documents/?level=' + currentFolder.id
    );
  });

  it('updateFolder call api', () => {
    axios.get.mockResolvedValue(mockedGetFoldersResponse);
    let currentFolder = tv.FOLDER_PROPS_VARIANT;

    // when
    wrapper.vm.updateFolder(currentFolder);

    // then
    expect(axios.get).toHaveBeenCalledWith(
      '/app/api/v1/folders/?level=' + currentFolder.id
    );
  });

  it('createNewFolder call api', done => {
    axios.post.mockResolvedValue(mockedPostFolderResponse);
    wrapper.setData({newFolderName: tv.FOLDER_PROPS.name});

    // when
    wrapper.vm.createNewFolder();

    // then
    expect(axios.post).toHaveBeenCalledWith(
      '/app/api/v1/folders/',
      {name: wrapper.vm.newFolderName, parent: null},
      axiosConfig
    );
    wrapper.vm.$nextTick(() => {
      expect(mockedRefreshFolder).toHaveBeenCalled();
      done();
    });
  });

  it('generateMissingThumbnail', async () => {
    const mockedGetDocumentFlat1 = {
      data: {
        count: 3,
        next: "http://localhost/next",
        previous: null,
        results: [{
          "pid": "gen-doc-1",
          "title": "abc.pdf",
          "note": "",
          "created": "2019-05-28T10:06:38.776392Z",
          "edited": "2019-05-28T10:07:02.316422Z",
          "ftl_folder": null,
          "thumbnail_available": true
        }, {
          "pid": "gen-doc-2",
          "title": "def.pdf",
          "note": "",
          "created": "2019-05-25T23:23:40.877590Z",
          "edited": "2019-05-28T10:06:22.003025Z",
          "ftl_folder": null,
          "thumbnail_available": true
        }]
      },
      status: 200,
    };

    const mockedGetDocumentFlat2 = {
      data: Promise.resolve({
        count: 3,
        next: null,
        previous: "http://localhost/previous",
        results: [{
          "pid": "gen-doc-3",
          "title": "ghi.pdf",
          "note": "",
          "created": "2019-05-28T10:06:38.776392Z",
          "edited": "2019-05-28T10:07:02.316422Z",
          "ftl_folder": null,
          "thumbnail_available": false
        }]
      }),
      status: 200,
    };

    axios.get.mockResolvedValueOnce(mockedGetDocumentFlat1);
    axios.get.mockResolvedValueOnce(mockedGetDocumentFlat2);
    axios.patch.mockResolvedValue({});

    createThumbFromUrl.mockResolvedValue("base64str");

    wrapper.vm.generateMissingThumbnail();
    await flushPromises();

    expect(axios.get).toHaveBeenCalledWith("/app/api/v1/documents?flat=true");
    expect(axios.get).toHaveBeenCalledWith("http://localhost/next");
    expect(axios.patch).toHaveBeenCalledWith(
      '/app/api/v1/documents/gen-doc-3',
      {'thumbnail_binary': 'base64str'},
      axiosConfig
    );
  })
});

describe('App event handling', () => {
  let wrapper;

  beforeEach(() => {
    wrapper = shallowMount(App, {
      localVue,
      methods: {
        changeFolder: mockedChangeFolder,
        updateDocument: mockedUpdateDocument,
        openDocument: mockedOpenDocument,
      }
    });
  });

  it('event-new-upload call updateDocument', done => {
    // when
    wrapper.find(FTLUpload).vm.$emit('event-new-upload');

    // then
    wrapper.vm.$nextTick(() => {
      expect(mockedUpdateDocument).toHaveBeenCalled();
      done();
    });
  });

  it('event-change-folder call changeFolder', done => {
    // Need to define at least one folder in order FTLFolder component is instantiated
    wrapper.setData({folders: [tv.FOLDER_PROPS]});
    let next_folder = tv.FOLDER_PROPS_VARIANT;

    // when
    wrapper.find(FTLFolder).vm.$emit('event-change-folder', next_folder);

    // then
    wrapper.vm.$nextTick(() => {
      expect(mockedChangeFolder).toHaveBeenCalledWith(next_folder);
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

  it('event-delete-doc call updateDocument', done => {
    // Need to define at least one document in order FTLDocument component is instantiated
    wrapper.setData({docs: [tv.DOCUMENT_PROPS]});

    // when
    wrapper.find(FTLDocument).vm.$emit('event-delete-doc');

    // then
    wrapper.vm.$nextTick(() => {
      expect(mockedUpdateDocument).toHaveBeenCalled();
      done();
    });
  });
});
