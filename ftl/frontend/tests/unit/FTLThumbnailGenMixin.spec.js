/*
 * Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
 * Licensed under the BSL License. See LICENSE in the project root for license information.
 */

import { createLocalVue, shallowMount } from "@vue/test-utils";
import FTLThumbnailGenMixin from "@/components/FTLThumbnailGenMixin";
import BootstrapVue from "bootstrap-vue";
import axios from "axios";
import { axiosConfig } from "../../src/constants";
import { createThumbFromUrl } from "../../src/thumbnailGenerator";
import * as tv from "./../tools/testValues.js";
import flushPromises from "flush-promises"; // needed for async tests

const localVue = createLocalVue();
localVue.use(BootstrapVue); // to avoid warning on tests execution
localVue.component("font-awesome-icon", jest.fn()); // avoid font awesome warning
localVue.prototype.$t = (text) => {
  return text;
}; // i18n mock
localVue.prototype.$tc = (text, args = "") => {
  return text + args;
}; // i18n mock
localVue.prototype.$moment = () => {
  return { fromNow: jest.fn() };
};
localVue.prototype.$router = { push: jest.fn() }; // router mock
const mockedMixinAlert = jest.fn();
localVue.mixin({ methods: { mixinAlert: mockedMixinAlert } }); // mixin alert

jest.mock("../../src/thumbnailGenerator", () => ({
  __esModule: true,
  createThumbFromUrl: jest.fn(),
}));

jest.mock("axios", () => ({
  get: jest.fn(),
  post: jest.fn(),
  patch: jest.fn(),
}));

const mockedUpdateDocumentResponse = {
  data: tv.DOCUMENT_PROPS,
  status: 200,
  config: axiosConfig,
};

describe("FTLThumbnailGenMixin methods", () => {
  let wrapper;
  axios.patch.mockResolvedValue(mockedUpdateDocumentResponse);
  beforeEach(() => {
    createThumbFromUrl.mockResolvedValue("base64str");
    wrapper = shallowMount(FTLThumbnailGenMixin, {
      localVue,
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("createThumbnailForDocument call proper methods and api", async () => {
    axios.patch.mockResolvedValue(mockedUpdateDocumentResponse);

    // when
    wrapper.vm.createThumbnailForDocument(tv.DOCUMENT_PROPS);
    await flushPromises();

    // then
    expect(createThumbFromUrl).toBeCalledTimes(1);
    expect(axios.patch).toBeCalledTimes(1);
    expect(axios.patch).toHaveBeenCalledWith(
      "/app/api/v1/documents/" + tv.DOCUMENT_PROPS.pid,
      { thumbnail_binary: "base64str" },
      axiosConfig
    );
  });

  it("createThumbnailForDocument handle error on createThumbFromUrl", async () => {
    // Expect a rejected promise is returned
    expect.assertions(1);

    // force createThumbFromUrl error
    createThumbFromUrl.mockRejectedValue("fakeError");

    // Test catch
    wrapper.vm
      .createThumbnailForDocument(tv.DOCUMENT_PROPS)
      .catch((e) => expect(e).toMatch("Unable to create thumbnail"));
    await flushPromises();
  });
});
