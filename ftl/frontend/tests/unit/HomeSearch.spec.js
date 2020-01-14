/*
 * Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
 * Licensed under the BSL License. See LICENSE in the project root for license information.
 */

import {createLocalVue, shallowMount} from '@vue/test-utils';

import axios from 'axios';
import BootstrapVue from "bootstrap-vue";
import flushPromises from "flush-promises"; // needed for async tests
import * as tv from './../tools/testValues.js'
import Vuex from 'vuex';

import HomeSearch from "../../src/views/HomeSearch";
import FTLUpload from "../../src/components/FTLUpload";
import FTLDocument from "../../src/components/FTLDocument";
import storeConfig from "@/store/storeConfig";
import cloneDeep from "lodash.clonedeep";
import FTLDocumentPanel from "@/components/FTLDocumentPanel";
import FTLDeleteDocuments from "@/components/FTLDeleteDocuments";
import FTLMoveDocuments from "@/components/FTLMoveDocuments";

const localVue = createLocalVue();
localVue.use(BootstrapVue); // to avoid warning on tests execution
localVue.use(Vuex);
localVue.component('font-awesome-icon', jest.fn()); // avoid font awesome warning
localVue.component('i18n', jest.fn());
localVue.prototype.$t = (text) => {
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

const mockedRefreshDocumentWithSearch = jest.fn();
const mockedUpdateDocuments = jest.fn();
const mocked_UpdateDocuments = jest.fn();
const mockedDocumentsCreated = jest.fn();
const mockedNavigateToDocument = jest.fn();
const mockedDocumentClosed = jest.fn();
const mockedDocumentUpdated = jest.fn();
const mockedDocumentDeleted = jest.fn();

const mountedMocks = {
  updateDocuments: mockedUpdateDocuments,
  refreshDocumentWithSearch: mockedRefreshDocumentWithSearch,
};

describe('HomeSearch template', () => {
  let wrapper;
  let storeConfigCopy;
  let store;
  beforeEach(() => {
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(storeConfigCopy);
    wrapper = shallowMount(HomeSearch, {
      localVue,
      store,
      methods: mountedMocks
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('renders properly home template', () => {
    expect(wrapper.text()).toContain('No document yet');
  });
});

describe('HomeSearch mounted call proper methods with given props', () => {
  let storeConfigCopy; // deep copy storeConfig for tests not to pollute it
  let store;
  beforeEach(() => {
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(storeConfigCopy);
    jest.clearAllMocks();
  });

  it('mounted call proper methods without props', () => {
    shallowMount(HomeSearch, {
      localVue,
      store,
      methods: mountedMocks,
    });

    // then
    expect(mockedUpdateDocuments).toHaveBeenCalledTimes(1);
    expect(mockedRefreshDocumentWithSearch).not.toHaveBeenCalled();
  });

  it('mounted call proper methods with searchQuery props', () => {
    const searchQuery = 'bingo!!';

    shallowMount(HomeSearch, {
      localVue,
      store,
      methods: mountedMocks,
      propsData: {searchQuery}
    });

    // then
    expect(mockedUpdateDocuments).not.toHaveBeenCalled();
    expect(mockedRefreshDocumentWithSearch).toHaveBeenCalledTimes(1);
    expect(mockedRefreshDocumentWithSearch).toHaveBeenCalledWith(searchQuery);
  });
});

describe('HomeSearch watchers call proper methods', () => {
  let wrapper;
  let storeConfigCopy; // deep copy storeConfig for tests not to pollute it
  let store;

  beforeEach(() => {
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(storeConfigCopy);
    wrapper = shallowMount(HomeSearch, {
      localVue,
      store,
      methods: mountedMocks,
    });
    jest.clearAllMocks();
  });

  it('searchQuery watcher call refreshDocumentWithSearch', async () => {
    const searchQuery = 'key words';

    //when
    wrapper.setData({searchQuery});

    await flushPromises();

    // then
    expect(mockedRefreshDocumentWithSearch).toHaveBeenCalledTimes(1);
    expect(mockedRefreshDocumentWithSearch).toHaveBeenCalledWith(searchQuery);
  });

  it('sort watcher call updateDocuments', async () => {
    const sort = 'fakeSort';

    //when
    wrapper.setData({sort});

    await flushPromises();

    // then
    expect(mockedUpdateDocuments).toHaveBeenCalledTimes(1);
  });
});

describe('HomeSearch methods', () => {
  let wrapper;
  let storeConfigCopy; // deep copy storeConfig for tests not to pollute it
  let store;
  let fakeUpdatedDocumentsValue;

  beforeEach(() => {
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(storeConfigCopy);
    fakeUpdatedDocumentsValue = 'fakeUpdatedDocuments';
    mocked_UpdateDocuments.mockReturnValue(fakeUpdatedDocumentsValue);
    wrapper = shallowMount(HomeSearch, {
      localVue,
      store,
      methods: Object.assign(
        mountedMocks,
        {_updateDocuments: mocked_UpdateDocuments}
        ),
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('refreshDocumentWithSearch call updateDocuments, set currentSearch and sort', () => {
    // restore original method to test it
    wrapper.setMethods({refreshDocumentWithSearch: HomeSearch.methods.refreshDocumentWithSearch});

    // when
    const searchQuery = 'coucou !';
    wrapper.vm.refreshDocumentWithSearch(searchQuery);

    // then
    expect(wrapper.vm.currentSearch).toBe(searchQuery);
    expect(wrapper.vm.sort).toBe('relevance');
    expect(mockedUpdateDocuments).toHaveBeenCalledTimes(1);
  });

  it('updateDocuments call _updateDocuments with currentSearch', () => {
    // restore original method to test it
    wrapper.setMethods({updateDocuments: HomeSearch.methods.updateDocuments});

    // when current search is not set
    wrapper.vm.updateDocuments();

    // then
    expect(mocked_UpdateDocuments).toHaveBeenCalledTimes(1);
    expect(mocked_UpdateDocuments).toHaveBeenCalledWith({});

    // when current search is set
    const currentSearch = 'bingo!';
    wrapper.setData({currentSearch});
    wrapper.vm.updateDocuments();

    // then
    expect(mocked_UpdateDocuments).toHaveBeenCalledTimes(2);
    expect(mocked_UpdateDocuments).toHaveBeenCalledWith({search: currentSearch});
  });

  it('updateDocuments return updated documents', () => {
    // restore original method to test it
    wrapper.setMethods({updateDocuments: HomeSearch.methods.updateDocuments});

    // when current search is not set
    const testedValue = wrapper.vm.updateDocuments();

    // then
    expect(testedValue).toEqual(fakeUpdatedDocumentsValue);
  });
});

describe('HomeSearch event handling', () => {
  let wrapper;
  let storeConfigCopy; // deep copy storeConfig for tests not to pollute it
  let store;

  beforeEach(() => {
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(Object.assign(
      {
        state: {
          selectedDocumentsHome: ['fakeDocument']
        },
        storeConfigCopy
      }
    ));
    wrapper = shallowMount(HomeSearch, {
      localVue,
      store,
      methods: Object.assign(
        {
          documentsCreated: mockedDocumentsCreated,
          navigateToDocument: mockedNavigateToDocument,
          documentClosed: mockedDocumentClosed,
          documentUpdated: mockedDocumentUpdated,
          documentDeleted: mockedDocumentDeleted,
        },
        mountedMocks
      ),
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
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
    expect(mockedDocumentClosed).toHaveBeenCalledTimes(1);
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
