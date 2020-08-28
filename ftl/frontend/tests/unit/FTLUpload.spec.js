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
import { FILES_PROPS } from "./../tools/testValues";

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

  it("renders properly html elem", () => {
    const elementSelector = "#upload-section";
    const elem = wrapper.find(elementSelector);
    expect(elem.is(elementSelector)).toBe(true);
  });
});

describe("FTLUpload methods", () => {
  const mockedPostResponse = {
    data: {},
    status: 201,
    config: axiosConfig,
  };
  let formData = new FormData();
  formData.append("file", tv.FILES_PROPS);
  formData.append("json", JSON.stringify({ ftl_folder: tv.FOLDER_PROPS.id }));
  formData.append("thumbnail", "base64str");
  let wrapper;
  let storeConfigCopy;
  let store;
  let getCurrentFolderMock = jest.fn();
  let uploadDocumentMock = jest.fn().mockResolvedValue("");
  const consumeUploadTasksMock = jest.fn();

  beforeEach(() => {
    axios.post.mockResolvedValue(mockedPostResponse);
    createThumbFromFile.mockResolvedValue("base64str");
    getCurrentFolderMock.mockReturnValue(tv.FOLDER_PROPS);

    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(storeConfigCopy);

    wrapper = shallowMount(FTLUpload, {
      localVue,
      store,
      computed: {
        getCurrentFolder: {
          get: getCurrentFolderMock,
          cache: false,
        },
      },
      methods: {
        uploadDocument: uploadDocumentMock,
        consumeUploadTasks: consumeUploadTasksMock,
      },
    });
  });

  it("addUploadTask set uploadTasks properly", async () => {
    // given user begin by selecting 1 file
    getCurrentFolderMock.mockReturnValue(tv.FOLDER_PROPS);
    wrapper.setData({
      selectedFiles: [tv.FILES_PROPS],
    });

    // when
    wrapper.vm.addUploadTask();

    // then
    let expectedUploadTasks = {};
    expectedUploadTasks[`id-${tv.FOLDER_PROPS.id}`] = {
      files: [tv.FILES_PROPS],
      folderName: tv.FOLDER_PROPS.name,
    };
    let expectedUploadTasksCompletedValue = {};
    expectedUploadTasksCompletedValue[`id-${tv.FOLDER_PROPS.id}`] = {
      folderName: tv.FOLDER_PROPS.name,
      successes: [],
      errors: [],
    };
    expect(wrapper.vm.uploadTasks).toEqual(expectedUploadTasks);
    expect(wrapper.vm.uploadTasksCompleted).toEqual(
      expectedUploadTasksCompletedValue
    );

    expect(wrapper.vm.selectedFiles).toEqual([]);

    // given user add 2 more docs to the same folder
    wrapper.setData({
      selectedFiles: [tv.FILES_PROPS_2, tv.FILES_PROPS_3],
    });

    // when
    wrapper.vm.addUploadTask();

    // then
    expectedUploadTasks = {};
    expectedUploadTasks[`id-${tv.FOLDER_PROPS.id}`] = {
      files: [tv.FILES_PROPS, tv.FILES_PROPS_2, tv.FILES_PROPS_3],
      folderName: tv.FOLDER_PROPS.name,
    };
    expectedUploadTasksCompletedValue = {};
    expectedUploadTasksCompletedValue[`id-${tv.FOLDER_PROPS.id}`] = {
      folderName: tv.FOLDER_PROPS.name,
      successes: [],
      errors: [],
    };
    expect(wrapper.vm.uploadTasks).toEqual(expectedUploadTasks);
    expect(wrapper.vm.uploadTasksCompleted).toEqual(
      expectedUploadTasksCompletedValue
    );

    expect(wrapper.vm.selectedFiles).toEqual([]);

    // given user add 3 more docs to another folder
    getCurrentFolderMock.mockReturnValue(tv.FOLDER_PROPS_VARIANT);
    wrapper.setData({
      selectedFiles: [tv.FILES_PROPS, tv.FILES_PROPS_2, tv.FILES_PROPS_3],
    });

    // when
    wrapper.vm.addUploadTask();

    // then
    expectedUploadTasks = {};
    expectedUploadTasks[`id-${tv.FOLDER_PROPS.id}`] = {
      files: [tv.FILES_PROPS, tv.FILES_PROPS_2, tv.FILES_PROPS_3],
      folderName: tv.FOLDER_PROPS.name,
    };
    expectedUploadTasks[`id-${tv.FOLDER_PROPS_VARIANT.id}`] = {
      files: [tv.FILES_PROPS, tv.FILES_PROPS_2, tv.FILES_PROPS_3],
      folderName: tv.FOLDER_PROPS_VARIANT.name,
    };
    expectedUploadTasksCompletedValue = {};
    expectedUploadTasksCompletedValue[`id-${tv.FOLDER_PROPS.id}`] = {
      folderName: tv.FOLDER_PROPS.name,
      successes: [],
      errors: [],
    };
    expectedUploadTasksCompletedValue[`id-${tv.FOLDER_PROPS_VARIANT.id}`] = {
      folderName: tv.FOLDER_PROPS_VARIANT.name,
      successes: [],
      errors: [],
    };
    expect(wrapper.vm.uploadTasks).toEqual(expectedUploadTasks);
    expect(wrapper.vm.uploadTasksCompleted).toEqual(
      expectedUploadTasksCompletedValue
    );

    expect(wrapper.vm.selectedFiles).toEqual([]);
  });

  it("consumeUploadTasks call uploadDocument properly", async () => {
    // restore original method to test it
    wrapper.setMethods({
      consumeUploadTasks: FTLUpload.methods.consumeUploadTasks,
    });
    // given there is 3 uploadTasks waiting
    let uploadTasks = {};
    uploadTasks[`id-${tv.FOLDER_PROPS.id}`] = {
      files: [tv.FILES_PROPS],
      folderName: tv.FOLDER_PROPS.name,
    };
    uploadTasks[`id-${tv.FOLDER_PROPS_VARIANT.id}`] = {
      files: [tv.FILES_PROPS, tv.FILES_PROPS_2],
      folderName: tv.FOLDER_PROPS_VARIANT.name,
    };
    uploadTasks[`id-${tv.FOLDER_PROPS_WITH_PARENT.id}`] = {
      files: [tv.FILES_PROPS, tv.FILES_PROPS_2, tv.FILES_PROPS_3],
      folderName: tv.FOLDER_PROPS_WITH_PARENT.name,
    };
    let uploadTasksCompleted = {};
    uploadTasksCompleted[`id-${tv.FOLDER_PROPS.id}`] = {
      folderName: tv.FOLDER_PROPS.name,
      successes: [],
      errors: [],
    };
    uploadTasksCompleted[`id-${tv.FOLDER_PROPS_VARIANT.id}`] = {
      folderName: tv.FOLDER_PROPS_VARIANT.name,
      successes: [],
      errors: [],
    };
    uploadTasksCompleted[`id-${tv.FOLDER_PROPS_WITH_PARENT.id}`] = {
      folderName: tv.FOLDER_PROPS_WITH_PARENT.name,
      successes: [],
      errors: [],
    };
    wrapper.setData({ uploadTasksCompleted, uploadTasks });

    // when
    await wrapper.vm.consumeUploadTasks();

    // then
    expect(uploadDocumentMock).toHaveBeenNthCalledWith(
      1,
      tv.FOLDER_PROPS.id,
      tv.FILES_PROPS
    );
    expect(uploadDocumentMock).toHaveBeenNthCalledWith(
      2,
      tv.FOLDER_PROPS_VARIANT.id,
      tv.FILES_PROPS
    );
    expect(uploadDocumentMock).toHaveBeenNthCalledWith(
      3,
      tv.FOLDER_PROPS_VARIANT.id,
      tv.FILES_PROPS_2
    );
    expect(uploadDocumentMock).toHaveBeenNthCalledWith(
      4,
      tv.FOLDER_PROPS_WITH_PARENT.id,
      tv.FILES_PROPS
    );
    expect(uploadDocumentMock).toHaveBeenNthCalledWith(
      5,
      tv.FOLDER_PROPS_WITH_PARENT.id,
      tv.FILES_PROPS_2
    );
    expect(uploadDocumentMock).toHaveBeenNthCalledWith(
      6,
      tv.FOLDER_PROPS_WITH_PARENT.id,
      tv.FILES_PROPS_3
    );

    let expectedUploadTasksCompleted = {};
    expectedUploadTasksCompleted[`id-${tv.FOLDER_PROPS.id}`] = {
      folderName: tv.FOLDER_PROPS.name,
      successes: [tv.FILES_PROPS.path],
      errors: [],
    };
    expectedUploadTasksCompleted[`id-${tv.FOLDER_PROPS_VARIANT.id}`] = {
      folderName: tv.FOLDER_PROPS_VARIANT.name,
      successes: [tv.FILES_PROPS.path, tv.FILES_PROPS_2.path],
      errors: [],
    };
    expectedUploadTasksCompleted[`id-${tv.FOLDER_PROPS_WITH_PARENT.id}`] = {
      folderName: tv.FOLDER_PROPS_WITH_PARENT.name,
      successes: [
        tv.FILES_PROPS.path,
        tv.FILES_PROPS_2.path,
        tv.FILES_PROPS_3.path,
      ],
      errors: [],
    };
    expect(wrapper.vm.uploadTasksCompleted).toEqual(
      expectedUploadTasksCompleted
    );

    // given user add additional upload tasks for 2 folders where task is already completed
    uploadTasks = {};
    uploadTasks[`id-${tv.FOLDER_PROPS.id}`] = {
      files: [tv.FILES_PROPS_2, tv.FILES_PROPS_3],
      folderName: tv.FOLDER_PROPS.name,
    };
    uploadTasks[`id-${tv.FOLDER_PROPS_VARIANT.id}`] = {
      files: [tv.FILES_PROPS_3],
      folderName: tv.FOLDER_PROPS_VARIANT.name,
    };
    wrapper.setData({ uploadTasks });

    // when
    await wrapper.vm.consumeUploadTasks();

    // then
    expect(uploadDocumentMock).toHaveBeenNthCalledWith(
      7,
      tv.FOLDER_PROPS.id,
      tv.FILES_PROPS_2
    );
    expect(uploadDocumentMock).toHaveBeenNthCalledWith(
      8,
      tv.FOLDER_PROPS.id,
      tv.FILES_PROPS_3
    );
    expect(uploadDocumentMock).toHaveBeenNthCalledWith(
      9,
      tv.FOLDER_PROPS_VARIANT.id,
      tv.FILES_PROPS_3
    );
    expectedUploadTasksCompleted = {};
    expectedUploadTasksCompleted[`id-${tv.FOLDER_PROPS.id}`] = {
      folderName: tv.FOLDER_PROPS.name,
      successes: [
        tv.FILES_PROPS.path,
        tv.FILES_PROPS_2.path,
        tv.FILES_PROPS_3.path,
      ],
      errors: [],
    };
    expectedUploadTasksCompleted[`id-${tv.FOLDER_PROPS_VARIANT.id}`] = {
      folderName: tv.FOLDER_PROPS_VARIANT.name,
      successes: [
        tv.FILES_PROPS.path,
        tv.FILES_PROPS_2.path,
        tv.FILES_PROPS_3.path,
      ],
      errors: [],
    };
    expectedUploadTasksCompleted[`id-${tv.FOLDER_PROPS_WITH_PARENT.id}`] = {
      folderName: tv.FOLDER_PROPS_WITH_PARENT.name,
      successes: [
        tv.FILES_PROPS.path,
        tv.FILES_PROPS_2.path,
        tv.FILES_PROPS_3.path,
      ],
      errors: [],
    };
    expect(wrapper.vm.uploadTasksCompleted).toEqual(
      expectedUploadTasksCompleted
    );
  });

  it("consumeUploadTasks handle uploadDOcument error", async () => {
    // restore original method to test it
    wrapper.setMethods({
      consumeUploadTasks: FTLUpload.methods.consumeUploadTasks,
    });
    // given there is 3 uploadTasks waiting
    let uploadTasks = {};
    uploadTasks[`id-${tv.FOLDER_PROPS.id}`] = {
      files: [tv.FILES_PROPS],
      folderName: tv.FOLDER_PROPS.name,
    };
    uploadTasks[`id-${tv.FOLDER_PROPS_VARIANT.id}`] = {
      files: [tv.FILES_PROPS, tv.FILES_PROPS_2],
      folderName: tv.FOLDER_PROPS_VARIANT.name,
    };
    uploadTasks[`id-${tv.FOLDER_PROPS_WITH_PARENT.id}`] = {
      files: [tv.FILES_PROPS, tv.FILES_PROPS_2, tv.FILES_PROPS_3],
      folderName: tv.FOLDER_PROPS_WITH_PARENT.name,
    };
    let uploadTasksCompleted = {};
    uploadTasksCompleted[`id-${tv.FOLDER_PROPS.id}`] = {
      folderName: tv.FOLDER_PROPS.name,
      successes: [],
      errors: [],
    };
    uploadTasksCompleted[`id-${tv.FOLDER_PROPS_VARIANT.id}`] = {
      folderName: tv.FOLDER_PROPS_VARIANT.name,
      successes: [],
      errors: [],
    };
    uploadTasksCompleted[`id-${tv.FOLDER_PROPS_WITH_PARENT.id}`] = {
      folderName: tv.FOLDER_PROPS_WITH_PARENT.name,
      successes: [],
      errors: [],
    };
    wrapper.setData({ uploadTasksCompleted, uploadTasks });
    // and uploadDocument reject
    uploadDocumentMock.mockRejectedValue("boom!");

    // when
    await wrapper.vm.consumeUploadTasks();

    // then
    expect(uploadDocumentMock).toHaveBeenNthCalledWith(
      1,
      tv.FOLDER_PROPS.id,
      tv.FILES_PROPS
    );
    expect(uploadDocumentMock).toHaveBeenNthCalledWith(
      2,
      tv.FOLDER_PROPS_VARIANT.id,
      tv.FILES_PROPS
    );
    expect(uploadDocumentMock).toHaveBeenNthCalledWith(
      3,
      tv.FOLDER_PROPS_VARIANT.id,
      tv.FILES_PROPS_2
    );
    expect(uploadDocumentMock).toHaveBeenNthCalledWith(
      4,
      tv.FOLDER_PROPS_WITH_PARENT.id,
      tv.FILES_PROPS
    );
    expect(uploadDocumentMock).toHaveBeenNthCalledWith(
      5,
      tv.FOLDER_PROPS_WITH_PARENT.id,
      tv.FILES_PROPS_2
    );
    expect(uploadDocumentMock).toHaveBeenNthCalledWith(
      6,
      tv.FOLDER_PROPS_WITH_PARENT.id,
      tv.FILES_PROPS_3
    );

    let expectedUploadTasksCompleted = {};
    expectedUploadTasksCompleted[`id-${tv.FOLDER_PROPS.id}`] = {
      folderName: tv.FOLDER_PROPS.name,
      successes: [],
      errors: [tv.FILES_PROPS],
    };
    expectedUploadTasksCompleted[`id-${tv.FOLDER_PROPS_VARIANT.id}`] = {
      folderName: tv.FOLDER_PROPS_VARIANT.name,
      successes: [],
      errors: [tv.FILES_PROPS, tv.FILES_PROPS_2],
    };
    expectedUploadTasksCompleted[`id-${tv.FOLDER_PROPS_WITH_PARENT.id}`] = {
      folderName: tv.FOLDER_PROPS_WITH_PARENT.name,
      successes: [],
      errors: [tv.FILES_PROPS, tv.FILES_PROPS_2, tv.FILES_PROPS_3],
    };
    expect(wrapper.vm.uploadTasksCompleted).toEqual(
      expectedUploadTasksCompleted
    );
  });

  it("uploadDocument call api", async () => {
    // restore original method to test it
    wrapper.setMethods({ uploadDocument: FTLUpload.methods.uploadDocument });
    // when
    wrapper.vm.uploadDocument(tv.FOLDER_PROPS.id, tv.FILES_PROPS);

    await flushPromises();
    // then
    expect(axios.post).toHaveBeenCalledTimes(1);
    expect(axios.post.mock.calls[0][0]).toEqual("/app/api/v1/documents/upload");
    expect(Array.from(axios.post.mock.calls[0][1])).toEqual(
      Array.from(formData)
    );
    expect(axios.post.mock.calls[0][2]).toEqual(axiosConfig);
  });
  it("uploadDocument call createThumbFromFile", async () => {
    wrapper.setMethods({ uploadDocument: FTLUpload.methods.uploadDocument });
    // when
    wrapper.vm.uploadDocument(tv.FOLDER_PROPS.id, tv.FILES_PROPS);

    await flushPromises();
    // then
    expect(createThumbFromFile).toHaveBeenCalled();
  });
  it("uploadDocument emit event-new-upload", async () => {
    wrapper.setMethods({ uploadDocument: FTLUpload.methods.uploadDocument });
    // when
    wrapper.vm.uploadDocument(tv.FOLDER_PROPS.id, tv.FILES_PROPS);

    await flushPromises();
    // then
    expect(wrapper.emitted("event-new-upload")).toBeTruthy();
  });
});
