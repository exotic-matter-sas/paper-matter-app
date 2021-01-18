/*
 * Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
 * Licensed under the Business Source License. See LICENSE at project root for more information.
 */

import { createLocalVue, shallowMount } from "@vue/test-utils";

import axios from "axios";
import BootstrapVue from "bootstrap-vue";
import flushPromises from "flush-promises"; // needed for async tests
import * as tv from "./../tools/testValues.js";
import { axiosConfig } from "../../src/constants";
import PDFObject from "pdfobject";

import FTLDocumentPanel from "../../src/components/FTLDocumentPanel";
import FTLNote from "@/components/FTLNote";
import FTLRenameDocument from "@/components/FTLRenameDocument";
import FTLMoveDocuments from "@/components/FTLMoveDocuments";
import cloneDeep from "lodash.clonedeep";
import storeConfig from "@/store/storeConfig";
import Vuex from "vuex";
import FTLDocumentSharing from "@/components/FTLDocumentSharing";

// Create clean Vue instance and set installed package to avoid warning
const localVue = createLocalVue();

// Mock BootstrapVue prototypes here (eg. localVue.prototype.$bvModal = {msgBoxConfirm: jest.fn()}; )
localVue.prototype.$bvModal = { show: jest.fn(), hide: jest.fn() };
localVue.use(BootstrapVue); // avoid bootstrap vue warnings
localVue.use(Vuex);
localVue.component("font-awesome-icon", jest.fn()); // avoid font awesome warnings

// Mock prototype and mixin bellow
localVue.prototype.$t = (text, args = "") => {
  return text + args;
}; // i18n mock
localVue.prototype.$tc = (text, args = "") => {
  return text + args;
}; // i18n mock
localVue.prototype.$store = { commit: jest.fn() }; // vuex mock
localVue.prototype.$moment = {
  parseZone: () => {
    return {
      format: jest.fn(),
      fromNow: jest.fn(),
    };
  },
}; // moment mock
localVue.prototype.$router = { push: jest.fn() }; // router mock
const mockedRoutePath = jest.fn();
localVue.prototype.$route = {
  get path() {
    return mockedRoutePath();
  },
}; // router mock
const mockedMixinAlert = jest.fn();
localVue.mixin({ methods: { mixinAlert: mockedMixinAlert } }); // mixinAlert mock

// mock calls to api requests
jest.mock("axios", () => ({
  get: jest.fn(),
}));

// mock PDFObject
jest.mock("pdfobject", () => ({
  embed: jest.fn(),
}));

const mockedGetDocumentResponse = {
  data: tv.DOCUMENT_PROPS,
  status: 200,
  config: axiosConfig,
};

const mockedGetDocumentNoThumbResponse = {
  data: tv.DOCUMENT_NO_THUMB_PROPS,
  status: 200,
  config: axiosConfig,
};

const mockedOpenDocument = jest.fn();
const mockedCreateThumbnailForDocument = jest.fn();
const mockedDocumentNoteUpdated = jest.fn();
const mockedDocumentRenamed = jest.fn();
const mockedDocumentShared = jest.fn();

const mountedMocks = {
  openDocument: mockedOpenDocument,
};

const docProps = tv.DOCUMENT_PROPS;

// TEMPLATE
describe("FTLDocumentPanel template", () => {
  let wrapper;
  let storeConfigCopy = cloneDeep(storeConfig);
  let store = new Vuex.Store(storeConfigCopy);
  // defined const specific to this describe here
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(FTLDocumentPanel, {
      localVue,
      store,
      methods: mountedMocks,
      propsData: { pid: docProps.pid },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("renders properly html element", () => {
    const elementSelector = "#document-viewer";
    const elem = wrapper.find(elementSelector);
    expect(elem.is(elementSelector)).toBe(true);
  });

  it("renders properly document title", async () => {
    wrapper.setData({ currentOpenDoc: docProps });
    expect(wrapper.text()).toContain(docProps.title);
  });
});

// MOUNTED
describe("FTLDocumentPanel mounted", () => {
  let wrapper;
  let storeConfigCopy = cloneDeep(storeConfig);
  let store = new Vuex.Store(storeConfigCopy);

  it("mounted call openDocument", () => {
    wrapper = shallowMount(FTLDocumentPanel, {
      localVue,
      store,
      methods: mountedMocks,
      propsData: { pid: docProps.pid },
    });

    expect(mockedOpenDocument).toBeCalledTimes(1);
  });
});

// COMPUTED
describe("FTLDocumentPanel computed", () => {
  let wrapper;
  let storeConfigCopy = cloneDeep(storeConfig);
  let store = new Vuex.Store(storeConfigCopy);
  let userAgentMock = jest
    .fn()
    .mockReturnValue(
      "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1"
    );
  Object.defineProperty(window.navigator, "userAgent", { get: userAgentMock });
  // defined const specific to this describe here
  beforeEach(() => {
    wrapper = shallowMount(FTLDocumentPanel, {
      localVue,
      store,
      methods: mountedMocks,
      propsData: { pid: docProps.pid, search: "my search" },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("isIOS return proper value", async () => {
    let testedResult = wrapper.vm.isIOS;

    expect(testedResult).toBe(true);
    // FIXME cant test more than one user agent, test not working if userAgent value is set after beforeEach (even with computed cache to false)
  });
});

// METHODS
describe("FTLDocumentPanel methods", () => {
  let wrapper;
  let storeConfigCopy = cloneDeep(storeConfig);
  let store = new Vuex.Store(storeConfigCopy);
  // defined const specific to this describe here
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(FTLDocumentPanel, {
      localVue,
      store,
      methods: Object.assign(
        { createThumbnailForDocument: mockedCreateThumbnailForDocument },
        mountedMocks
      ),
      propsData: { pid: docProps.pid },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("openDocument call api", async () => {
    // restore original method to test it
    wrapper.setMethods({ openDocument: FTLDocumentPanel.methods.openDocument });
    axios.get.mockResolvedValue(mockedGetDocumentResponse);

    // when
    wrapper.vm.openDocument();
    await flushPromises();

    // then
    expect(axios.get).toBeCalledWith("/app/api/v1/documents/" + docProps.pid);
    expect(axios.get).toBeCalledTimes(1);
  });

  it("openDocument call mixinAlert in case of API error", async () => {
    // restore original method to test it
    wrapper.setMethods({ openDocument: FTLDocumentPanel.methods.openDocument });
    // force an API error
    axios.get.mockRejectedValue("fakeError");

    // when
    wrapper.vm.openDocument();
    await flushPromises();

    // then mixinAlert is called with proper message
    expect(mockedMixinAlert).toBeCalledTimes(1);
    expect(mockedMixinAlert.mock.calls[0][0]).toContain("document");
  });

  it("openDocument call createThumbnailForDocument if thumbnail not available", async () => {
    axios.get.mockResolvedValue(mockedGetDocumentNoThumbResponse);
    // restore original method to test it
    wrapper.setMethods({ openDocument: FTLDocumentPanel.methods.openDocument });

    // when
    wrapper.vm.openDocument();
    await flushPromises();

    // then
    expect(mockedCreateThumbnailForDocument).toBeCalledTimes(1);
  });

  it("openDocument call mixinAlert in case of API error of createThumbnailForDocument", async () => {
    axios.get.mockResolvedValue(mockedGetDocumentNoThumbResponse);
    mockedCreateThumbnailForDocument.mockRejectedValue("fakeError");
    // restore original method to test it
    wrapper.setMethods({ openDocument: FTLDocumentPanel.methods.openDocument });

    // when
    wrapper.vm.openDocument();
    await flushPromises();

    // then mixinAlert is called with proper message
    expect(mockedMixinAlert).toBeCalledTimes(1);
    expect(mockedMixinAlert.mock.calls[0][0]).toContain("thumbnail");
  });

  it("openDocument set currentOpenDoc and show document-viewer modal", async () => {
    axios.get.mockResolvedValue(mockedGetDocumentResponse);
    // restore original method to test it
    wrapper.setMethods({ openDocument: FTLDocumentPanel.methods.openDocument });

    // when
    wrapper.vm.openDocument();
    await flushPromises();

    // then mixinAlert is called with proper message
    expect(wrapper.vm.currentOpenDoc).toEqual(mockedGetDocumentResponse.data);
    expect(wrapper.vm.$bvModal.show).toBeCalledTimes(1);
    expect(wrapper.vm.$bvModal.show).toBeCalledWith("document-viewer");
  });

  it("documentRenamed set currentOpenDoc", async () => {
    // when
    wrapper.vm.documentRenamed({ doc: docProps });
    await flushPromises();

    // then
    expect(wrapper.vm.currentOpenDoc).toEqual(docProps);
  });

  it("documentRenamed emit event-document-renamed", async () => {
    const testedEvent = "event-document-renamed";
    // when
    wrapper.vm.documentRenamed({ doc: docProps });
    await flushPromises();

    // then
    expect(wrapper.emitted(testedEvent)).toBeTruthy();
    expect(wrapper.emitted(testedEvent).length).toBe(1);
    expect(wrapper.emitted(testedEvent)[0]).toEqual([{ doc: docProps }]);
  });

  it("documentNoteUpdated set currentOpenDoc", async () => {
    // when
    wrapper.vm.documentNoteUpdated({ doc: docProps });
    await flushPromises();

    // then
    expect(wrapper.vm.currentOpenDoc).toEqual(docProps);
  });

  it("documentShared set currentOpenDoc.is_shared", async () => {
    // when
    wrapper.vm.documentShared(true);

    // then
    expect(wrapper.vm.currentOpenDoc.is_shared).toEqual(true);

    // when
    wrapper.vm.documentShared(false);

    // then
    expect(wrapper.vm.currentOpenDoc.is_shared).toEqual(false);
  });

  it("closeDocument reset currentOpenDoc and hide document-viewer modal", async () => {
    // given
    wrapper.setData({ currentOpenDoc: tv.DOCUMENT_PROPS });

    // when
    wrapper.vm.closeDocument();
    await flushPromises();

    // then
    expect(wrapper.vm.currentOpenDoc).toEqual({ path: [] });
    expect(wrapper.vm.$bvModal.hide).toBeCalledTimes(1);
    expect(wrapper.vm.$bvModal.hide).toBeCalledWith("document-viewer");
  });

  it("closeDocument emit event-document-panel-closed", async () => {
    const testedEvent = "event-document-panel-closed";
    // when
    wrapper.vm.closeDocument();
    await flushPromises();

    // then
    expect(wrapper.emitted(testedEvent)).toBeTruthy();
    expect(wrapper.emitted(testedEvent).length).toBe(1);
  });

  it("closeDocument restore previous path", async () => {
    const previousPathValue = "fakePreviousPath";
    mockedRoutePath.mockReturnValue(previousPathValue);
    // when
    wrapper.vm.closeDocument();
    await flushPromises();

    // then
    expect(wrapper.vm.$router.push).toHaveBeenCalledTimes(1);
    expect(wrapper.vm.$router.push).toHaveBeenCalledWith(
      { path: previousPathValue },
      expect.any(Function)
    );
  });

  it("embedDoc call PDFObject embedding method", async () => {
    // given
    const search_text = "my search";
    const document_pid = docProps.pid;
    wrapper.setData({ currentOpenDoc: docProps });
    wrapper.setProps({ pid: document_pid, search: search_text });
    wrapper.setMethods({ embedDoc: FTLDocumentPanel.methods.embedDoc });
    PDFObject.embed.mockReturnValue(true);

    wrapper.vm.embedDoc();

    const options = {
      PDFJS_URL: "/assets/pdfjs/web/viewer.html",
      supportRedirect: true,
      forcePDFJS: false,
      omitInlineStyles: true,
      pdfOpenParams: {
        pagemode: "none",
        search: search_text,
      },
    };

    expect(PDFObject.embed).toBeCalledWith(
      tv.DOCUMENT_PROPS.download_url + "/open",
      "#pdf-embed-container",
      options
    );

    expect(PDFObject.embed).toBeCalledTimes(1);
  });
});

// EVENT
describe("Event received and handled by component", () => {
  let wrapper;
  let storeConfigCopy = cloneDeep(storeConfig);
  let store = new Vuex.Store(storeConfigCopy);
  // defined const specific to this describe here
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(FTLDocumentPanel, {
      localVue,
      store,
      methods: Object.assign(
        {
          documentNoteUpdated: mockedDocumentNoteUpdated,
          documentRenamed: mockedDocumentRenamed,
          documentShared: mockedDocumentShared,
        },
        mountedMocks
      ),
      propsData: { pid: docProps.pid },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("event-document-note-edited call documentNoteUpdated", async () => {
    // currentOpenDoc need to be set for FTLNote to be instantiated
    wrapper.setData({ currentOpenDoc: tv.DOCUMENT_PROPS_VARIANT });
    const eventArg = { doc: docProps };
    // when (called by event)
    wrapper.find(FTLNote).vm.$emit("event-document-note-edited", eventArg);

    // then method called
    expect(mockedDocumentNoteUpdated).toHaveBeenCalledWith(eventArg);
  });
  it("event-document-moved re-emit event-document-moved", async () => {
    const testedEvent = "event-document-moved";
    // currentOpenDoc need to be set for FTLMoveDocuments to be instantiated
    wrapper.setData({ currentOpenDoc: tv.DOCUMENT_PROPS_VARIANT });
    const eventArg = { doc: docProps };
    // when (called by event)
    wrapper.find(FTLMoveDocuments).vm.$emit(testedEvent, eventArg);

    // then event re-emit by FTLDocumentPanel
    expect(wrapper.emitted(testedEvent)).toBeTruthy();
    expect(wrapper.emitted(testedEvent).length).toBe(1);
    expect(wrapper.emitted(testedEvent)[0]).toEqual([eventArg]);
  });
  it("event-document-renamed call documentRenamed", async () => {
    // currentOpenDoc need to be set for FTLRenameDocument to be instantiated
    wrapper.setData({ currentOpenDoc: tv.DOCUMENT_PROPS_VARIANT });
    const eventArg = { doc: docProps };
    // when (called by event)
    wrapper
      .find(FTLRenameDocument)
      .vm.$emit("event-document-renamed", eventArg);

    // then method called
    expect(mockedDocumentRenamed).toHaveBeenCalledWith(eventArg);
  });
  it("event-document-shared call documentShared", async () => {
    // currentOpenDoc need to be set for FTLRenameDocument to be instantiated
    wrapper.setData({ currentOpenDoc: tv.DOCUMENT_PROPS });
    // when (called by event)
    wrapper.find(FTLDocumentSharing).vm.$emit("event-document-shared");

    // then method called
    expect(mockedDocumentShared).toHaveBeenCalledWith(true);
  });
  it("event-document-unshared call documentShared", async () => {
    // currentOpenDoc need to be set for FTLRenameDocument to be instantiated
    wrapper.setData({ currentOpenDoc: tv.DOCUMENT_PROPS });
    // when (called by event)
    wrapper.find(FTLDocumentSharing).vm.$emit("event-document-unshared");

    // then method called
    expect(mockedDocumentShared).toHaveBeenCalledWith(false);
  });
});
