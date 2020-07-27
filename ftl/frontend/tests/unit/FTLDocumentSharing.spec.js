/*
 * Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
 * Licensed under the BSL License. See LICENSE in the project root for license information.
 */

import { createLocalVue, shallowMount } from "@vue/test-utils";

import axios from "axios";
import BootstrapVue from "bootstrap-vue";
import flushPromises from "flush-promises"; // needed for async tests

import * as tv from "./../tools/testValues.js";
import { axiosConfig } from "../../src/constants";

import FTLDocumentSharing from "../../src/components/FTLDocumentSharing";

// Create clean Vue instance and set installed package to avoid warning
const localVue = createLocalVue();

// Mock BootstrapVue prototypes here (eg. localVue.prototype.$bvModal = {msgBoxConfirm: jest.fn()}; )
localVue.prototype.$bvModal = { show: jest.fn(), hide: jest.fn() };
localVue.use(BootstrapVue); // avoid bootstrap vue warnings
localVue.component("font-awesome-icon", jest.fn()); // avoid font awesome warnings

// Mock prototype and mixin bellow
localVue.prototype.$t = (text, args = "") => {
  return text + args;
}; // i18n mock
localVue.prototype.$tc = (text, args = "") => {
  return text + args;
}; // i18n mock
const mockedMixinAlert = jest.fn();
localVue.mixin({ methods: { mixinAlert: mockedMixinAlert } }); // mixinAlert mock

// mock calls to api requests
jest.mock("axios", () => ({
  get: jest.fn(),
  post: jest.fn(),
  delete: jest.fn()
}));

const mockedGetDocumentShareLinksResponse = {
  data: {
    count: 2,
    next: null,
    previous: null,
    results: [tv.DOCUMENT_SHARE_LINK, tv.DOCUMENT_SHARE_LINK_VARIANT]
  },
  status: 200,
  config: axiosConfig,
};

const mockedGetDocumentShareLinksEmptyResponse = {
  data: {
    count: 0,
    next: null,
    previous: null,
    results: []
  },
  status: 200,
  config: axiosConfig,
};

const mockedPostDocumentShareLink = {
  data: tv.DOCUMENT_SHARE_LINK,
  status: 201,
  config: axiosConfig,
};

const mockedDeleteDocumentShareLink = {
  status: 204,
  config: axiosConfig,
};

// TEMPLATE
describe("FTLDocumentSharing template", () => {
  let wrapper;
  // defined const specific to this describe here
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(FTLDocumentSharing, {
      localVue,
      propsData: {
        doc: tv.DOCUMENT_PROPS
      }
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("renders properly text", () => {
    expect(wrapper.text()).toContain("Copy to clipboard");
  });
  it("renders properly html element", () => {
    const elementSelector = "#modal-document-sharing";
    const elem = wrapper.find(elementSelector);
    expect(elem.is(elementSelector)).toBe(true);
  });
});

// COMPUTED
describe("FTLDocumentSharing computed", () => {
  let wrapper;
  // defined const specific to this describe here
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(FTLDocumentSharing, {
      localVue,
      propsData: {
        doc: tv.DOCUMENT_PROPS
      },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("sharingLink return proper format", () => {
    // given shareData default value

    // when
    let testedResult = wrapper.vm.sharingLink;

    // then
    expect(testedResult).toEqual('');

    // given shareData has a public_url set
    wrapper.setData({ shareData: { public_url: 'fakePublicUrl'}});

    // when
    testedResult = wrapper.vm.sharingLink;

    // then
    expect(testedResult).toEqual('fakePublicUrl');
  });
});

// METHODS
describe("FTLDocumentSharing methods", () => {
  let wrapper;
  let clipboardWriteTextMock = jest.fn().mockResolvedValue('');
  // defined const specific to this describe here
  beforeEach(() => {
    axios.post.mockResolvedValue(mockedPostDocumentShareLink);
    axios.delete.mockResolvedValue(mockedDeleteDocumentShareLink);
    Object.assign(navigator, {
      clipboard: {
        writeText: clipboardWriteTextMock,
      },
    });
    jest.spyOn(navigator.clipboard, "writeText");    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(FTLDocumentSharing, {
      localVue,
      propsData: {
        doc: tv.DOCUMENT_PROPS
      }
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("doSharing call api and emit event properly", async () => {
    // given share links already exist for document
    axios.get.mockResolvedValue(mockedGetDocumentShareLinksResponse);

    // when
    wrapper.vm.doSharing();
    await flushPromises();

    // then
    expect(axios.get).toHaveBeenNthCalledWith(
      1,
      `/app/api/v1/documents/${tv.DOCUMENT_PROPS.pid}/share`,
      axiosConfig
    );
    expect(axios.post).toHaveBeenCalledTimes(0);
    // UI only display first share link for now
    expect(wrapper.vm.shareData).toEqual(mockedGetDocumentShareLinksResponse.data.results[0]);

    // given no share link exist for document
    axios.get.mockResolvedValue(mockedGetDocumentShareLinksEmptyResponse);
    jest.clearAllMocks();

    // when
    wrapper.vm.doSharing();
    await flushPromises();

    // then
    expect(axios.get).toHaveBeenCalledTimes(1);
    expect(axios.post).toHaveBeenNthCalledWith(
      1,
      `/app/api/v1/documents/${tv.DOCUMENT_PROPS.pid}/share`,
      {},
      axiosConfig
    );
    // UI display the link just created
    expect(wrapper.vm.shareData).toEqual(mockedPostDocumentShareLink.data);
    // also emit event-document-shared event
    expect(wrapper.emitted("event-document-shared")).toBeTruthy();
    expect(wrapper.emitted("event-document-shared").length).toBe(1);
  });
  it("doSharing handle api error", async () => {
    // given get request reject an error
    axios.get.mockRejectedValue('Boom');

    // when
    wrapper.vm.doSharing();
    await flushPromises();

    // then mixinAlert is called with proper message
    expect(mockedMixinAlert).toBeCalledTimes(1);
    expect(mockedMixinAlert.mock.calls[0][0]).toContain("share link");

    // given post request reject an error
    axios.get.mockResolvedValue(mockedGetDocumentShareLinksEmptyResponse);
    axios.post.mockRejectedValue('Boom');
    jest.clearAllMocks();

    // when
    wrapper.vm.doSharing();
    await flushPromises();

    // then mixinAlert is called with proper message
    expect(mockedMixinAlert).toBeCalledTimes(1);
    expect(mockedMixinAlert.mock.calls[0][0]).toContain("share document");
  });
  it("cancelSharing call api and emit event properly", async () => {
    // given delete request resolve and shareData is set
    wrapper.setData({ shareData: tv.DOCUMENT_SHARE_LINK });

    // when
    wrapper.vm.cancelSharing();
    await flushPromises();

    // then
    expect(axios.delete).toHaveBeenNthCalledWith(
      1,
      `/app/api/v1/documents/${tv.DOCUMENT_PROPS.pid}/share/${tv.DOCUMENT_SHARE_LINK.pid}`,
      axiosConfig
    );
    // UI only display first share link for now
    expect(wrapper.emitted("event-document-unshared")).toBeTruthy();
    expect(wrapper.emitted("event-document-unshared").length).toBe(1);
  });
  it("cancelSharing handle api error", async () => {
    // given delete request reject an error
    axios.delete.mockRejectedValue('Boom');

    // when
    wrapper.vm.cancelSharing();
    await flushPromises();

    // then mixinAlert is called with proper message
    expect(mockedMixinAlert).toBeCalledTimes(1);
    expect(mockedMixinAlert.mock.calls[0][0]).toContain("unshare document");
  });
  it("copyClipboard call navigator.clipboard and close modal", async () => {
    // given delete request resolve and shareData is set
    wrapper.setData({ shareData: tv.DOCUMENT_SHARE_LINK });

    // when
    wrapper.vm.copyClipboard();
    await flushPromises();

    // then
    expect(clipboardWriteTextMock).toHaveBeenNthCalledWith(
      1,
      tv.DOCUMENT_SHARE_LINK.public_url
    );
    expect(wrapper.vm.$bvModal.hide).toHaveBeenNthCalledWith(
      1,
      "modal-document-sharing"
    );
  });
});
