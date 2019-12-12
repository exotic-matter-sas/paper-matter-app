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

import FTLDocumentPanel from "../../src/components/FTLDocumentPanel";
import FTLNote from "@/components/FTLNote";
import FTLRenameDocument from "@/components/FTLRenameDocument";
import FTLMoveDocuments from "@/components/FTLMoveDocuments";

// Create clean Vue instance and set installed package to avoid warning
const localVue = createLocalVue();

// Mock BootstrapVue prototypes here (eg. localVue.prototype.$bvModal = {msgBoxConfirm: jest.fn()}; )
localVue.prototype.$bvModal = {show: jest.fn(), hide: jest.fn()};
localVue.use(BootstrapVue); // avoid bootstrap vue warnings
localVue.component('font-awesome-icon', jest.fn()); // avoid font awesome warnings

// Mock prototype and mixin bellow
localVue.prototype.$_ = (text, args='') => {return text + args};// i18n mock
localVue.prototype.$moment = () => {return {fromNow: jest.fn(), format: jest.fn()}}; // moment mock
localVue.prototype.$router = {push: jest.fn()}; // router mock
const mockedRoutePath = jest.fn();
localVue.prototype.$route = {get path() { return mockedRoutePath()}}; // router mock
const mockedMixinAlert = jest.fn();
localVue.mixin({methods: {mixinAlert: mockedMixinAlert}}); // mixinAlert mock

// mock calls to api requests
jest.mock('axios', () => ({
  get: jest.fn(),
}));

const mockedGetDocumentResponse = {
  data: tv.DOCUMENT_PROPS,
  status: 200,
  config: axiosConfig
};

const mockedGetDocumentNoThumbResponse = {
  data: tv.DOCUMENT_NO_THUMB_PROPS,
  status: 200,
  config: axiosConfig
};

const mockedOpenDocument = jest.fn();
const mockedCreateThumbnailForDocument = jest.fn();
const mockedDocumentNoteUpdated = jest.fn();
const mockedDocumentRenamed = jest.fn();

const mountedMocks = {
  openDocument: mockedOpenDocument,
};

const docProps = tv.DOCUMENT_PROPS;

// TEMPLATE
describe('FTLDocumentPanel template', () => {
  let wrapper;
  // defined const specific to this describe here
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(FTLDocumentPanel, {
      localVue,
      methods: mountedMocks,
      propsData: { pid: docProps.pid},
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('renders properly html element', () => {
    const elementSelector= '#document-viewer';
    const elem = wrapper.find(elementSelector);
    expect(elem.is(elementSelector)).toBe(true);
  });

  it('renders properly document title', async () => {
    wrapper.setData({currentOpenDoc: docProps});
    expect(wrapper.text()).toContain(docProps.title);
  });
});

// MOUNTED
describe('FTLDocumentPanel mounted', () => {
  let wrapper;

  it('mounted call openDocument', () => {
    wrapper = shallowMount(FTLDocumentPanel, {
      localVue,
      methods: mountedMocks,
      propsData: { pid: docProps.pid},
    });

    expect(mockedOpenDocument).toBeCalledTimes(1);
  });
});

// COMPUTED
describe('FTLDocumentPanel computed', () => {
  let wrapper;
  // defined const specific to this describe here
  beforeEach(() => {
    wrapper = shallowMount(FTLDocumentPanel, {
      localVue,
      methods: mountedMocks,
      propsData: {pid: docProps.pid},
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('isIOS return proper value', async () => {
    // TODO test main iOS user agent device here when we will be able to force recompute of computed
  });
});

// METHODS
describe('FTLDocumentPanel methods', () => {
  let wrapper;
  // defined const specific to this describe here
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(FTLDocumentPanel, {
      localVue,
      methods: Object.assign(
        {createThumbnailForDocument: mockedCreateThumbnailForDocument},
        mountedMocks
      ),
      propsData: { pid: docProps.pid},
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('openDocument call api', async () => {
    // restore original method to test it
    wrapper.setMethods({openDocument: FTLDocumentPanel.methods.openDocument});
    axios.get.mockResolvedValue(mockedGetDocumentResponse);

    // when
    wrapper.vm.openDocument();
    await flushPromises();

    // then
    expect(axios.get).toBeCalledWith('/app/api/v1/documents/' + docProps.pid);
    expect(axios.get).toBeCalledTimes(1);
  });

  it('openDocument call mixinAlert in case of API error', async () => {
    // restore original method to test it
    wrapper.setMethods({openDocument: FTLDocumentPanel.methods.openDocument});
    // force an API error
    axios.get.mockRejectedValue('fakeError');

    // when
    wrapper.vm.openDocument();
    await flushPromises();

    // then mixinAlert is called with proper message
    expect(mockedMixinAlert).toBeCalledTimes(1);
    expect(mockedMixinAlert.mock.calls[0][0]).toContain('document');
  });

  it('openDocument call createThumbnailForDocument if thumbnail not available', async () => {
    axios.get.mockResolvedValue(mockedGetDocumentNoThumbResponse);
    // restore original method to test it
    wrapper.setMethods({openDocument: FTLDocumentPanel.methods.openDocument});

    // when
    wrapper.vm.openDocument();
    await flushPromises();

    // then
    expect(mockedCreateThumbnailForDocument).toBeCalledTimes(1);
  });

  it('openDocument call mixinAlert in case of API error of createThumbnailForDocument', async () => {
    axios.get.mockResolvedValue(mockedGetDocumentNoThumbResponse);
    mockedCreateThumbnailForDocument.mockRejectedValue('fakeError');
    // restore original method to test it
    wrapper.setMethods({openDocument: FTLDocumentPanel.methods.openDocument});

    // when
    wrapper.vm.openDocument();
    await flushPromises();

    // then mixinAlert is called with proper message
    expect(mockedMixinAlert).toBeCalledTimes(1);
    expect(mockedMixinAlert.mock.calls[0][0]).toContain('thumbnail');
  });

  it('openDocument set currentOpenDoc and show document-viewer modal', async () => {
    axios.get.mockResolvedValue(mockedGetDocumentResponse);
    // restore original method to test it
    wrapper.setMethods({openDocument: FTLDocumentPanel.methods.openDocument});

    // when
    wrapper.vm.openDocument();
    await flushPromises();

    // then mixinAlert is called with proper message
    expect(wrapper.vm.currentOpenDoc).toEqual(mockedGetDocumentResponse.data);
    expect(wrapper.vm.$bvModal.show).toBeCalledTimes(1);
    expect(wrapper.vm.$bvModal.show).toBeCalledWith('document-viewer');
  });

  it('documentRenamed set currentOpenDoc', async () => {
    // when
    wrapper.vm.documentRenamed({doc: docProps});
    await flushPromises();

    // then
    expect(wrapper.vm.currentOpenDoc).toEqual(docProps);
  });

  it('documentRenamed emit event-document-renamed', async () => {
    const testedEvent = 'event-document-renamed';
    // when
    wrapper.vm.documentRenamed({doc: docProps});
    await flushPromises();

    // then
    expect(wrapper.emitted(testedEvent)).toBeTruthy();
    expect(wrapper.emitted(testedEvent).length).toBe(1);
    expect(wrapper.emitted(testedEvent)[0]).toEqual([{doc: docProps}]);
  });

  it('documentNoteUpdated set currentOpenDoc', async () => {
    // when
    wrapper.vm.documentNoteUpdated({doc: docProps});
    await flushPromises();

    // then
    expect(wrapper.vm.currentOpenDoc).toEqual(docProps);
  });

  it('closeDocument reset currentOpenDoc and hide document-viewer modal', async () => {
    // given
    wrapper.setData({currentOpenDoc: tv.DOCUMENT_PROPS});

    // when
    wrapper.vm.closeDocument();
    await flushPromises();

    // then
    expect(wrapper.vm.currentOpenDoc).toEqual({});
    expect(wrapper.vm.$bvModal.hide).toBeCalledTimes(1);
    expect(wrapper.vm.$bvModal.hide).toBeCalledWith('document-viewer');
  });

  it('closeDocument emit event-document-panel-closed', async () => {
    const testedEvent = 'event-document-panel-closed';
    // when
    wrapper.vm.closeDocument();
    await flushPromises();

    // then
    expect(wrapper.emitted(testedEvent)).toBeTruthy();
    expect(wrapper.emitted(testedEvent).length).toBe(1);
  });

  it('closeDocument restore previous path', async () => {
    const previousPathValue = 'fakePreviousPath';
    mockedRoutePath.mockReturnValue(previousPathValue);
    // when
    wrapper.vm.closeDocument();
    await flushPromises();

    // then
    expect(wrapper.vm.$router.push).toHaveBeenCalledTimes(1);
    expect(wrapper.vm.$router.push).toHaveBeenCalledWith({path: previousPathValue}, expect.any(Function));
  });
});

// EVENT
describe('Event received and handled by component', () => {
  let wrapper;
  // defined const specific to this describe here
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(FTLDocumentPanel, {
      localVue,
      methods: Object.assign(
        {
          documentNoteUpdated: mockedDocumentNoteUpdated,
          documentRenamed: mockedDocumentRenamed
        },
        mountedMocks
      ),
      propsData: { pid: docProps.pid},
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('event-document-note-edited call documentNoteUpdated', async () => {
    // currentOpenDoc need to be set for FTLNote to be instantiated
    wrapper.setData({currentOpenDoc: tv.DOCUMENT_PROPS_VARIANT});
    const eventArg = {doc: docProps};
    // when (called by event)
    wrapper.find(FTLNote).vm.$emit('event-document-note-edited', eventArg);

    // then method called
    expect(mockedDocumentNoteUpdated).toHaveBeenCalledWith(eventArg);
  });
  it('event-document-moved re-emit event-document-moved', async () => {
    const testedEvent = 'event-document-moved';
    // currentOpenDoc need to be set for FTLMoveDocuments to be instantiated
    wrapper.setData({currentOpenDoc: tv.DOCUMENT_PROPS_VARIANT});
    const eventArg = {doc: docProps};
    // when (called by event)
    wrapper.find(FTLMoveDocuments).vm.$emit(testedEvent, eventArg);

    // then event re-emit by FTLDocumentPanel
    expect(wrapper.emitted(testedEvent)).toBeTruthy();
    expect(wrapper.emitted(testedEvent).length).toBe(1);
    expect(wrapper.emitted(testedEvent)[0]).toEqual([eventArg]);
  });
  it('event-document-renamed call documentRenamed', async () => {
    // currentOpenDoc need to be set for FTLRenameDocument to be instantiated
    wrapper.setData({currentOpenDoc: tv.DOCUMENT_PROPS_VARIANT});
    const eventArg = {doc: docProps};
    // when (called by event)
    wrapper.find(FTLRenameDocument).vm.$emit('event-document-renamed', eventArg);

    // then method called
    expect(mockedDocumentRenamed).toHaveBeenCalledWith(eventArg);
  });
});
