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

import HomeBase from "../../src/views/HomeBase";
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
const mockedRoutePath = jest.fn();
localVue.prototype.$route = {
  get path() {
    return mockedRoutePath()
  }
};
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

const mockedOpenDocument = jest.fn();
const mockedUpdateDocuments = jest.fn();
const mockedUnselectDocumentMutation = jest.fn();

const mountedMocks = {
  openDocument: mockedOpenDocument
};

describe('HomeBase mounted call proper methods with given props', () => {
  let storeConfigCopy; // deep copy storeConfig for tests not to pollute it
  let store;
  beforeEach(() => {
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(storeConfigCopy);
    jest.clearAllMocks();
  });

  it('mounted call no method without doc props', () => {
    shallowMount(HomeBase, {
      localVue,
      store,
      methods: mountedMocks,
    });

    // then
    expect(mockedOpenDocument).not.toHaveBeenCalled();
  });

  it('mounted call proper methods with doc props', () => {
    shallowMount(HomeBase, {
      localVue,
      store,
      methods: mountedMocks,
      propsData: {doc: tv.DOCUMENT_PROPS}
    });

    // then
    expect(mockedOpenDocument).toHaveBeenCalledTimes(1);
  });
});

describe('HomeBase watchers call proper methods', () => {
  let wrapper;
  let storeConfigCopy; // deep copy storeConfig for tests not to pollute it
  let store;

  beforeEach(() => {
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(storeConfigCopy);
    wrapper = shallowMount(HomeBase, {
      localVue,
      store,
      methods: mountedMocks,
    });
    jest.clearAllMocks();
  });

  it('doc watcher call openDocument if doc value not undefined', () => {
    // when doc is defined
    let doc = tv.DOCUMENT_PROPS.pid;
    wrapper.setData({doc});

    // then
    expect(mockedOpenDocument).toHaveBeenCalledTimes(1);
    expect(mockedOpenDocument).toHaveBeenCalledWith(doc);

    // when doc is reset to undefined
    jest.clearAllMocks();
    doc = undefined;
    wrapper.setData({doc});

    // then
    expect(wrapper.vm.docModal).toBe(false);
    expect(mockedOpenDocument).not.toHaveBeenCalled();
  });
});

describe('HomeBase methods call proper methods', () => {
  let wrapper;
  let storeConfigCopy; // deep copy storeConfig for tests not to pollute it
  let store;
  const fakePath =
    tv.FOLDER_PROPS.name + '/'
    + tv.FOLDER_PROPS_VARIANT.name + '/'
    + tv.FOLDER_PROPS_VARIANT.id;

  beforeEach(() => {
    mockedRoutePath.mockReturnValue(fakePath);
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(storeConfigCopy);
    wrapper = shallowMount(HomeBase, {
      localVue,
      store,
      methods: Object.assign(
        {updateDocuments: mockedUpdateDocuments},
        mountedMocks
      )
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('documentClosed set docPid to null', () => {
    wrapper.setData({docPid:tv.DOCUMENT_PROPS.pid});

    // when
    wrapper.vm.documentClosed({doc: tv.DOCUMENT_PROPS});

    // then
    expect(wrapper.vm.docPid).toBe(null);
    expect(wrapper.vm.$router.push).toHaveBeenNthCalledWith(1, {path: fakePath});
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

describe('HomeBase methods error handling', () => {
  let wrapper;
  let storeConfigCopy; // deep copy storeConfig for tests not to pollute it
  let store;

  beforeEach(() => {
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(storeConfigCopy);
    wrapper = shallowMount(HomeBase, {
      localVue,
      store,
      methods: mountedMocks
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('_updateDocuments call mixinAlert in case of api error', async () => {
    axios.get.mockRejectedValue('error');
    wrapper.setData({previousLevels: [tv.FOLDER_PROPS, tv.FOLDER_PROPS_VARIANT]});

    // when
    wrapper.vm._updateDocuments();
    await flushPromises(); // wait all pending promises are resolved/rejected

    // then
    expect(mockedMixinAlert).toHaveBeenCalledTimes(1);
  });

  it('loadMoreDocuments call mixinAlert in case of api error', async () => {
    axios.get.mockRejectedValue('error');

    // when
    wrapper.vm.loadMoreDocuments();
    await flushPromises(); // wait all pending promises are resolved/rejected

    // then
    expect(mockedMixinAlert).toHaveBeenCalledTimes(1);
  });
});

describe('HomeBase methods call proper api', () => {
  let wrapper;
  let storeConfigCopy; // deep copy storeConfig for tests not to pollute it
  let store;

  beforeEach(() => {
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(storeConfigCopy);
    wrapper = shallowMount(HomeBase, {
        localVue,
        store,
        methods: mountedMocks
      }
    );
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('_updateDocuments call api with sorting older', () => {
    wrapper.setData({sort: 'older'});

    axios.get.mockResolvedValue(mockedGetDocumentsResponse);

    // when
    wrapper.vm._updateDocuments();

    // then
    expect(axios.get).toHaveBeenCalledWith('/app/api/v1/documents?ordering=created');
    expect(axios.get).toHaveBeenCalledTimes(1);
  });

  it('_updateDocuments call api with sorting az', () => {
    wrapper.setData({sort: 'az'});

    axios.get.mockResolvedValue(mockedGetDocumentsResponse);

    // when
    wrapper.vm._updateDocuments();

    // then
    expect(axios.get).toHaveBeenCalledWith('/app/api/v1/documents?ordering=title');
    expect(axios.get).toHaveBeenCalledTimes(1);
  });

  it('_updateDocuments call api with sorting za', () => {
    wrapper.setData({sort: 'za'});

    axios.get.mockResolvedValue(mockedGetDocumentsResponse);

    // when
    wrapper.vm._updateDocuments();

    // then
    expect(axios.get).toHaveBeenCalledWith('/app/api/v1/documents?ordering=-title');
    expect(axios.get).toHaveBeenCalledTimes(1);
  });

  it('loadMoreDocuments call api', () => {
    axios.get.mockResolvedValue(mockedGetDocumentsResponse);
    const fakeMoreDocsurlValue = 'fakeMoreDocsurl';
    wrapper.setData({moreDocs: fakeMoreDocsurlValue});

    // when
    wrapper.vm.loadMoreDocuments();

    // then
    expect(axios.get).toHaveBeenCalledWith(fakeMoreDocsurlValue);
    expect(axios.get).toHaveBeenCalledTimes(1);
  });
});

describe('HomeBase methods update proper data', () => {
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
            unselectDocument: mockedUnselectDocumentMutation
          }
        }
      )
    );    wrapper = shallowMount(HomeBase, {
      localVue,
      store,
      methods: Object.assign(
        {updateDocuments: mockedUpdateDocuments},
        mountedMocks
      )
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

  it('openDocument update docPid', () => {
    // restore original method to test it
    const fakeDocPidValue = 123;
    wrapper.setMethods({openDocument: HomeBase.methods.openDocument});

    // when
    wrapper.vm.openDocument(fakeDocPidValue);

    // then
    expect(wrapper.vm.docPid).toBe(fakeDocPidValue);
  });

  it('documentDeleted commit unselectDocument to store', () => {
    // when
    const fakeDoc = tv.DOCUMENT_PROPS;
    wrapper.vm.documentDeleted({doc:fakeDoc});

    // then
    expect(mockedUnselectDocumentMutation).toBeCalledTimes(1);
    expect(mockedUnselectDocumentMutation).toBeCalledWith(storeConfigCopy.state, fakeDoc);
  });
});
