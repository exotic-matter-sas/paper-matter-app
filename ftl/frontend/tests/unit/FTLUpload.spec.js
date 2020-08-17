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
  let uploadDocumentMock = jest.fn().mockResolvedValue("");

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
      },
      methods: {
        uploadDocument: uploadDocumentMock
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

  it("consumeUploadTasks call api and set uploadTasksCompleted properly", async () => {
    // given there is 3 uploadTasks waiting
    wrapper.setData({
      uploadTasks: new Map([
        [tv.FOLDER_PROPS.id, [tv.FILES_PROPS]],
        [tv.FOLDER_PROPS_VARIANT.id, [tv.FILES_PROPS, tv.FILES_PROPS_2]],
        [tv.FOLDER_PROPS_WITH_PARENT.id, [tv.FILES_PROPS, tv.FILES_PROPS_2, tv.FILES_PROPS_3]],
      ])
    });

    // when
    await wrapper.vm.consumeUploadTasks();

    // then
    expect(uploadDocumentMock).toHaveBeenNthCalledWith(1, tv.FOLDER_PROPS.id, tv.FILES_PROPS);
    expect(uploadDocumentMock).toHaveBeenNthCalledWith(2, tv.FOLDER_PROPS_VARIANT.id, tv.FILES_PROPS);
    expect(uploadDocumentMock).toHaveBeenNthCalledWith(3, tv.FOLDER_PROPS_VARIANT.id, tv.FILES_PROPS_2);
    expect(uploadDocumentMock).toHaveBeenNthCalledWith(4, tv.FOLDER_PROPS_WITH_PARENT.id, tv.FILES_PROPS);
    expect(uploadDocumentMock).toHaveBeenNthCalledWith(5, tv.FOLDER_PROPS_WITH_PARENT.id, tv.FILES_PROPS_2);
    expect(uploadDocumentMock).toHaveBeenNthCalledWith(6, tv.FOLDER_PROPS_WITH_PARENT.id, tv.FILES_PROPS_3);
    expect(wrapper.vm.uploadTasksCompleted).toEqual(new Map([
      [tv.FOLDER_PROPS.id, {successes: [tv.FILES_PROPS.path], errors: []}],
      [tv.FOLDER_PROPS_VARIANT.id, {successes: [tv.FILES_PROPS.path, tv.FILES_PROPS_2.path], errors: []}],
      [tv.FOLDER_PROPS_WITH_PARENT.id, {successes: [tv.FILES_PROPS.path, tv.FILES_PROPS_2.path, tv.FILES_PROPS_3.path], errors: []}],
    ]));

    // given user add additional upload tasks for 2 folders where task is already completed
    wrapper.setData({
      uploadTasks: new Map([
        [tv.FOLDER_PROPS.id, [tv.FILES_PROPS_2, tv.FILES_PROPS_3]],
        [tv.FOLDER_PROPS_VARIANT.id, [tv.FILES_PROPS_3]],
      ])
    });

    // when
    await wrapper.vm.consumeUploadTasks();

    // then
    expect(uploadDocumentMock).toHaveBeenNthCalledWith(7, tv.FOLDER_PROPS.id, tv.FILES_PROPS_2);
    expect(uploadDocumentMock).toHaveBeenNthCalledWith(8, tv.FOLDER_PROPS.id, tv.FILES_PROPS_3);
    expect(uploadDocumentMock).toHaveBeenNthCalledWith(9, tv.FOLDER_PROPS_VARIANT.id, tv.FILES_PROPS_3);
    expect(wrapper.vm.uploadTasksCompleted).toEqual(new Map([
      [tv.FOLDER_PROPS.id, {successes: [tv.FILES_PROPS.path, tv.FILES_PROPS_2.path, tv.FILES_PROPS_3.path], errors: []}],
      [tv.FOLDER_PROPS_VARIANT.id, {successes: [tv.FILES_PROPS.path, tv.FILES_PROPS_2.path, tv.FILES_PROPS_3.path], errors: []}],
      [tv.FOLDER_PROPS_WITH_PARENT.id, {successes: [tv.FILES_PROPS.path, tv.FILES_PROPS_2.path, tv.FILES_PROPS_3.path], errors: []}],
    ]));
  });

  it("consumeUploadTasks handle api error", async () => {
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
  });

  it("uploadDocument call api", async () => {
    // restore original method to test it
    wrapper.setMethods({ uploadDocument: FTLUpload.methods.uploadDocument });
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
    wrapper.setMethods({ uploadDocument: FTLUpload.methods.uploadDocument });
    // when
    wrapper.vm.uploadDocument();

    await flushPromises();
    // then
    expect(createThumbFromFile).toHaveBeenCalled();
  });
  it("uploadDocument emit event-new-upload", async () => {
    wrapper.setMethods({ uploadDocument: FTLUpload.methods.uploadDocument });
    // when
    wrapper.vm.uploadDocument();

    await flushPromises();
    // then
    expect(wrapper.emitted("event-new-upload")).toBeTruthy();
  });
});
