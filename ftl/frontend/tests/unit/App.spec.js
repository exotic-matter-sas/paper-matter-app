import { createLocalVue, shallowMount } from '@vue/test-utils';

import axios from 'axios';
import BootstrapVue from "bootstrap-vue";

import * as tv from './../tools/testValues.js'
import App from "../../src/App";
import FTLUpload from "../../src/components/FTLUpload";
import FTLFolder from "../../src/components/FTLFolder";
import FTLDocument from "../../src/components/FTLDocument";

const localVue = createLocalVue();
localVue.use(BootstrapVue); // to avoid warning on tests execution

jest.mock('axios', () => ({
    get: jest.fn()
}));

const mockedGetFoldersResponse  = {
  data: [],
  status: 200,
  config: tv.AXIOS_CRSF_CONF
};
const mockedGetDocumentsResponse  = {
  data: {results: []},
  status: 200,
  config: tv.AXIOS_CRSF_CONF
};
const mockedGetDocumentResponse  = {
  data: tv.DOCUMENT_PROPS,
  status: 200,
  config: tv.AXIOS_CRSF_CONF
};

const mockedUpdateFolder = jest.fn();
const mockedUpdateDocument = jest.fn();
const mockedChangeFolder = jest.fn();
const mockedOpenDocument = jest.fn();


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
    // when
    // view is mounted

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
    let currentFolder = tv.FOLDER_PROPS;

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
});

describe('App script methods call proper api', () => {
  let wrapper;

  beforeEach(() => {
    axios.get.mockReturnValueOnce(Promise.resolve(mockedGetFoldersResponse));
    axios.get.mockReturnValueOnce(Promise.resolve(mockedGetDocumentsResponse));
    wrapper = shallowMount(App, {localVue});
  });

  it('openDocument call api', () => {
    axios.get.mockReturnValue(Promise.resolve(mockedGetDocumentResponse));
    let opened_document_pid = tv.DOCUMENT_PROPS.pid;

    // when
    wrapper.vm.openDocument(opened_document_pid);

    // then
    expect(axios.get).toHaveBeenCalledWith(
        '/app/api/v1/documents/' + opened_document_pid
    );
  });

  it('updateDocument call api', () => {
    axios.get.mockReturnValue(Promise.resolve(mockedGetDocumentsResponse));
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
    axios.get.mockReturnValue(Promise.resolve(mockedGetFoldersResponse));
    let currentFolder = tv.FOLDER_PROPS_VARIANT;

    // when
    wrapper.vm.updateFolder(currentFolder);

    // then
    expect(axios.get).toHaveBeenCalledWith(
        '/app/api/v1/folders/?level=' + currentFolder.id
    );
  });
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