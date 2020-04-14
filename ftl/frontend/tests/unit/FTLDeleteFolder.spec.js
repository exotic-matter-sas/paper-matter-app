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

import FTLDeleteFolder from "../../src/components/FTLDeleteFolder";

// Create clean Vue instance and set installed package to avoid warning
const localVue = createLocalVue();
localVue.use(BootstrapVue); // avoid bootstrap vue warnings
localVue.component("font-awesome-icon", jest.fn()); // avoid font awesome warnings

// Mock prototype and mixin bellow
localVue.prototype.$t = (text, args = "") => {
  return text + args;
}; // i18n mock
localVue.prototype.$tc = (text, args = "") => {
  return text + args;
}; // i18n mock
localVue.prototype.$moment = () => {
  return { fromNow: jest.fn() };
}; // moment mock
const mockedMixinAlert = jest.fn();
localVue.mixin({ methods: { mixinAlert: mockedMixinAlert } }); // mixinAlert mock

// mock calls to api requests
jest.mock("axios", () => ({
  delete: jest.fn(),
}));

const mockedDeleteFolder = {
  status: 204,
};

const folderToDelete = tv.FOLDER_PROPS;

describe("FTLDeleteFolder template", () => {
  let wrapper;
  beforeEach(() => {
    wrapper = shallowMount(FTLDeleteFolder, {
      localVue,
      propsData: { folder: folderToDelete },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("renders properly FTLDeleteFolder data", () => {
    expect(wrapper.html()).toContain("Deletion of folder");
    expect(wrapper.html()).toContain(folderToDelete.name);
  });
});

describe("FTLDeleteFolder methods", () => {
  let wrapper;
  const mockedBvModalEvt = { preventDefault: jest.fn() };
  beforeEach(() => {
    axios.delete.mockResolvedValue(mockedDeleteFolder);
    wrapper = shallowMount(FTLDeleteFolder, {
      localVue,
      propsData: { folder: folderToDelete },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("deleteFolder call api", () => {
    const mockedBvModalEvt = { preventDefault: jest.fn() };

    // when
    wrapper.vm.deleteFolder(mockedBvModalEvt);

    // then
    expect(axios.delete).toHaveBeenCalledWith(
      "/app/api/v1/folders/" + folderToDelete.id,
      axiosConfig
    );
    expect(axios.delete).toHaveBeenCalledTimes(1);
  });

  it("deleteFolder emit event event-folder-deleted", async () => {
    const testedEvent = "event-folder-deleted";

    // when
    wrapper.vm.deleteFolder(mockedBvModalEvt);
    await flushPromises();

    // then
    expect(wrapper.emitted(testedEvent)).toBeTruthy();
    expect(wrapper.emitted(testedEvent).length).toBe(1);
    expect(wrapper.emitted(testedEvent)[0]).toEqual([
      { folder: folderToDelete },
    ]);
  });

  it("deleteFolder call mixinAlert in case of API error", async () => {
    axios.delete.mockRejectedValue("errorDescription");

    // when
    wrapper.vm.deleteFolder(mockedBvModalEvt);
    await flushPromises();

    // then
    expect(mockedMixinAlert).toHaveBeenCalledTimes(1);
    expect(mockedMixinAlert.mock.calls[0][0]).toContain("delete folder");
  });
});
