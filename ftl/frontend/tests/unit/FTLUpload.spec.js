/*
 * Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
 * Licensed under the BSL License. See LICENSE in the project root for license information.
 */

import { createLocalVue, shallowMount } from "@vue/test-utils";
import axios from "axios";
import BootstrapVue from "bootstrap-vue";
import * as tv from "./../tools/testValues.js";
import FTLUpload from "../../src/components/FTLUpload";
import flushPromises from "flush-promises";
import { axiosConfig } from "../../src/constants";
import { createThumbFromFile } from "../../src/thumbnailGenerator";
import cloneDeep from "lodash.clonedeep";
import storeConfig from "@/store/storeConfig";
import Vuex from "vuex";

const localVue = createLocalVue();
localVue.use(BootstrapVue); // to avoid warning on tests execution
localVue.use(Vuex);
localVue.prototype.$t = (text) => {
  return text;
}; // i18n mock
localVue.prototype.$tc = (text, args = "") => {
  return text + args;
}; // i18n mock
localVue.prototype.$moment = () => {
  return { fromNow: jest.fn() };
};
localVue.mixin({ methods: { mixinAlert: jest.fn() } }); // mixin alert

jest.mock("axios", () => ({
  post: jest.fn(),
}));

jest.mock("../../src/thumbnailGenerator", () => ({
  createThumbFromFile: jest.fn(),
}));

describe("FTLUpload template", () => {
  let storeConfigCopy;
  let store;

  storeConfigCopy = cloneDeep(storeConfig);
  store = new Vuex.Store(storeConfigCopy);

  const wrapper = shallowMount(FTLUpload, {
    localVue,
    store,
    propsData: { currentFolder: tv.FOLDER_PROPS },
  });

  it("renders properly upload UI", () => {
    expect(wrapper.html()).toContain("Upload document");
  });
});

describe("FTLUpload methods", () => {
  let axios_upload_conf;
  const mockedPostResponse = {
    data: {},
    status: 201,
    config: axiosConfig,
  };
  let formData = new FormData();
  formData.append("file", { type: "application/pdf" });
  formData.append("json", JSON.stringify({ ftl_folder: tv.FOLDER_PROPS.id }));
  formData.append("thumbnail", "base64str");
  let wrapper;
  let storeConfigCopy;
  let store;
  let currentFolderMock = jest.fn();

  beforeEach(() => {
    axios.post.mockResolvedValue(mockedPostResponse);
    createThumbFromFile.mockResolvedValue("base64str");
    currentFolderMock.mockReturnValue(tv.FOLDER_PROPS);

    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(storeConfigCopy);

    wrapper = shallowMount(FTLUpload, {
      localVue,
      store,
      computed: {
        currentFolder: {
          get: currentFolderMock,
          cache: false
        }
      }
    });
    axios_upload_conf = {
      onUploadProgress: wrapper.vm.refreshUploadProgression,
    };
    Object.assign(axios_upload_conf, axiosConfig); // merge upload specific conf with generic crsf conf
    wrapper.setData({ selectedFiles: [{ type: "application/pdf" }] });
  });

  it("addUploadTask set uploadTasks properly", async () => {
    // given user begin by selecting 1 file
    currentFolderMock.mockReturnValue(tv.FOLDER_PROPS);
    wrapper.setData({
      selectedFiles: [tv.FILES_PROPS]
    });

    // when
    wrapper.vm.addUploadTask();

    // then
    expect(wrapper.vm.uploadTasks).toEqual(new Map([
      [tv.FOLDER_PROPS.id, [tv.FILES_PROPS]],
    ]));
    expect(wrapper.vm.selectedFiles).toEqual([]);

    // given user add 2 more docs to the same folder
    wrapper.setData({
      selectedFiles: [tv.FILES_PROPS_2, tv.FILES_PROPS_3]
    });

    // when
    wrapper.vm.addUploadTask();

    // then
    expect(wrapper.vm.uploadTasks).toEqual(new Map([
      [tv.FOLDER_PROPS.id, [tv.FILES_PROPS, tv.FILES_PROPS_2, tv.FILES_PROPS_3]],
    ]));
    expect(wrapper.vm.selectedFiles).toEqual([]);

    // given user add 3 more docs to another folder
    currentFolderMock.mockReturnValue(tv.FOLDER_PROPS_VARIANT);
    wrapper.setData({
      selectedFiles: [tv.FILES_PROPS, tv.FILES_PROPS_2, tv.FILES_PROPS_3]
    });

    // when
    wrapper.vm.addUploadTask();

    // then
    expect(wrapper.vm.uploadTasks).toEqual(new Map([
      [tv.FOLDER_PROPS.id, [tv.FILES_PROPS, tv.FILES_PROPS_2, tv.FILES_PROPS_3]],
      [tv.FOLDER_PROPS_VARIANT.id, [tv.FILES_PROPS, tv.FILES_PROPS_2, tv.FILES_PROPS_3]],
    ]));
    expect(wrapper.vm.selectedFiles).toEqual([]);
  });

  it("uploadDocument call api", async () => {
    // when
    wrapper.vm.uploadDocument();

    await flushPromises();
    // then
    expect(axios.post).toHaveBeenCalledWith(
      "/app/api/v1/documents/upload",
      formData,
      axios_upload_conf
    );
  });
  it("uploadDocument call createThumbFromFile", async () => {
    // when
    wrapper.vm.uploadDocument();

    await flushPromises();
    // then
    expect(createThumbFromFile).toHaveBeenCalled();
  });
  it("uploadDocument emit event-new-upload", async () => {
    // when
    wrapper.vm.uploadDocument();

    await flushPromises();
    // then
    expect(wrapper.emitted("event-new-upload")).toBeTruthy();
  });
});
