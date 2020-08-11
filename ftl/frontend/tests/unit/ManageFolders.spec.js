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

import ManageFolders from "../../src/views/ManageFolders";
import FTLDeleteFolder from "../../src/components/FTLDeleteFolder";
import FTLRenameFolder from "../../src/components/FTLRenameFolder";
import FTLSelectableFolder from "../../src/components/FTLSelectableFolder";
import FTLNewFolder from "../../src/components/FTLNewFolder";
import FTLMoveFolder from "../../src/components/FTLMoveFolder";
import cloneDeep from "lodash.clonedeep";
import storeConfig from "@/store/storeConfig";
import Vuex from "vuex";

const localVue = createLocalVue();

localVue.use(BootstrapVue); // avoid bootstrap vue warnings
localVue.use(Vuex);
localVue.component("font-awesome-icon", jest.fn()); // avoid font awesome warnings

localVue.prototype.$t = (text, args = "") => {
  return text + args;
}; // i18n mock
localVue.prototype.$tc = (text, args = "") => {
  return text + args;
}; // i18n mock
localVue.prototype.$moment = () => {
  return { fromNow: jest.fn() };
}; // moment mock
const mockedRouterPush = jest.fn();
localVue.prototype.$router = { push: mockedRouterPush }; // router mock
const mockedMixinAlert = jest.fn();
localVue.mixin({ methods: { mixinAlert: mockedMixinAlert } }); // mixinAlert mock

// mock calls to api requests
jest.mock("axios", () => ({
  get: jest.fn(),
}));

const mockedGetFoldersListResponse = {
  data: [tv.FOLDER_PROPS, tv.FOLDER_PROPS_VARIANT],
  status: 200,
  config: axiosConfig,
};
const mockedGetFolderDetailsResponse = {
  data: { paths: "fakePath" },
  status: 200,
  config: axiosConfig,
};

const mockedRefreshFolder = jest.fn();
const mockedGetFolderDetail = jest.fn();
const mockedUnselectFolder = jest.fn();
const mockedNavigateToFolder = jest.fn();
const mockedUpdateFolders = jest.fn();
const mockedUpdateFoldersFromUrl = jest.fn();
const mockedBreadcrumb = jest.fn();
const mockedGetCurrentFolder = jest.fn();
const mockedFolderMoved = jest.fn();
const mockedFolderDeleted = jest.fn();
const mockedFolderUpdated = jest.fn();
const mockedFolderCreated = jest.fn();
const mockedFTLTreeItemSelected = jest.fn();
const mockedSelectMoveTargetFolder = jest.fn();

const mountedMocks = {
  updateFolders: mockedUpdateFolders,
  updateFoldersFromUrl: mockedUpdateFoldersFromUrl,
};

const folder = tv.FOLDER_PROPS;
const targetFolder = tv.FOLDER_PROPS_VARIANT;

describe("ManageFolders template", () => {
  let wrapper;
  // defined const specific to this describe here
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(ManageFolders, {
      localVue,
      methods: mountedMocks,
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("renders properly component template", () => {
    const elementSelector = "#folders-mngt";
    const elem = wrapper.find(elementSelector);

    expect(elem.is(elementSelector)).toBe(true);

    expect(wrapper.text()).toContain("No folder selected");
  });
});

describe("ManageFolders mounted call proper methods", () => {
  let wrapper;

  it("mounted without props call proper methods", () => {
    jest.clearAllMocks();
    //when mounted with folder props
    wrapper = shallowMount(ManageFolders, {
      localVue,
      methods: {
        updateFolders: mockedUpdateFolders,
      },
    });

    //then
    expect(mockedUpdateFolders).toHaveBeenCalledTimes(1);
  });

  it("mounted with folder props call proper methods", () => {
    jest.clearAllMocks();
    //when mounted with folder props
    wrapper = shallowMount(ManageFolders, {
      localVue,
      propsData: { folder },
      methods: {
        updateFoldersFromUrl: mockedUpdateFoldersFromUrl,
      },
    });

    //then
    expect(mockedUpdateFoldersFromUrl).toHaveBeenCalledTimes(1);
    expect(mockedUpdateFoldersFromUrl).toHaveBeenCalledWith(folder);
  });
});

describe("ManageFolders computed", () => {
  let wrapper;
  // defined const specific to this describe here
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(ManageFolders, {
      localVue,
      methods: mountedMocks,
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("getCurrentFolder return proper format", () => {
    // when previousLevels empty
    const testedReturn = wrapper.vm.getCurrentFolder;

    //then
    expect(testedReturn).toBe(null);
  });
  it("getCurrentFolder return proper format whe previousLevels set", () => {
    // when previousLevels set
    wrapper.setData({
      previousLevels: [tv.FOLDER_PROPS, tv.FOLDER_PROPS_VARIANT],
    });
    const testedReturn = wrapper.vm.getCurrentFolder;

    //then
    expect(testedReturn).toBe(tv.FOLDER_PROPS_VARIANT);
  });
  it("breadcrumb return proper format", () => {
    // when previousLevels set
    wrapper.setData({
      previousLevels: [tv.FOLDER_PROPS, tv.FOLDER_PROPS_VARIANT],
    });
    const testedReturn = wrapper.vm.breadcrumb;

    //then
    expect(testedReturn).toEqual([
      { text: "Root", to: { name: "folders" } },
      {
        text: tv.FOLDER_PROPS.name,
        to: { name: "folders", params: { folder: tv.FOLDER_PROPS.id } },
      },
      {
        text: tv.FOLDER_PROPS_VARIANT.name,
        to: { name: "folders", params: { folder: tv.FOLDER_PROPS_VARIANT.id } },
      },
    ]);
  });
});

describe("ManageFolders methods", () => {
  let wrapper;
  let storeConfigCopy;
  let store;
  beforeEach(() => {
    mockedFTLTreeItemSelected.mockReturnValue(false);
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(
      Object.assign(storeConfigCopy, {
        mutations: {
          selectMoveTargetFolder: mockedSelectMoveTargetFolder,
        },
        getters: {
          FTLTreeItemSelected: () => mockedFTLTreeItemSelected,
        },
      })
    );
    wrapper = shallowMount(ManageFolders, {
      localVue,
      store,
      methods: Object.assign(
        {
          unselectFolder: mockedUnselectFolder,
          refreshFolder: mockedRefreshFolder,
          navigateToFolder: mockedNavigateToFolder,
        },
        mountedMocks
      ),
      propsData: { folder },
      computed: {
        breadcrumb: mockedBreadcrumb,
        getCurrentFolder: mockedGetCurrentFolder,
      },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("refreshFolder call proper methods", () => {
    // restore original method to test it
    wrapper.setMethods({ refreshFolder: ManageFolders.methods.refreshFolder });

    //when called with folder props
    wrapper.vm.refreshFolder();

    //then
    expect(mockedUpdateFolders).not.toHaveBeenCalled();
    expect(mockedUpdateFoldersFromUrl).toHaveBeenCalledWith(folder);

    //when called without folder props
    jest.clearAllMocks();
    wrapper.setData({ folder: undefined });
    wrapper.vm.refreshFolder();

    //then
    expect(mockedUpdateFolders).toHaveBeenCalledTimes(1 + 1); //+1 for the call inside watch folder which isn't mockable
    expect(mockedUpdateFoldersFromUrl).not.toHaveBeenCalled();
  });
  it("unselectFolder update data", () => {
    // restore original method to test it
    wrapper.setMethods({
      unselectFolder: ManageFolders.methods.unselectFolder,
    });

    //when
    wrapper.setData({ folderDetail: tv.FOLDER_PROPS });
    wrapper.vm.unselectFolder();

    //then
    expect(wrapper.vm.folderDetail).toBe(null);
  });
  it("navigateToFolder push data to router", () => {
    wrapper.setData({ previousLevels: [tv.FOLDER_PROPS] });
    // restore original method to test it
    wrapper.setMethods({
      navigateToFolder: ManageFolders.methods.navigateToFolder,
    });

    //when
    wrapper.vm.navigateToFolder(tv.FOLDER_PROPS_VARIANT);

    //then
    expect(wrapper.vm.previousLevels).toEqual([
      tv.FOLDER_PROPS,
      tv.FOLDER_PROPS_VARIANT,
    ]);
    expect(mockedRouterPush).toHaveBeenCalledTimes(1);
    expect(mockedRouterPush).toHaveBeenCalledWith({
      name: "folders",
      params: { folder: tv.FOLDER_PROPS_VARIANT.id },
    });
  });
  it("updateFoldersFromUrl call propers methods", async () => {
    // restore original method to test it
    wrapper.setMethods({
      updateFoldersFromUrl: ManageFolders.methods.updateFoldersFromUrl,
    });
    axios.get.mockResolvedValueOnce(mockedGetFolderDetailsResponse);
    //when
    wrapper.vm.updateFoldersFromUrl(tv.FOLDER_PROPS.id);
    await flushPromises();

    //then
    expect(wrapper.vm.previousLevels).toBe(
      mockedGetFolderDetailsResponse.data.paths
    );
    expect(mockedUpdateFolders).toHaveBeenCalledTimes(1);
    expect(mockedUpdateFolders).toHaveBeenCalledWith(
      mockedGetFolderDetailsResponse.data
    );
  });
  it("folderCreated push folder to the list and set folder.highlightAnimation", () => {
    // given
    wrapper.setData({ folders: [tv.FOLDER_PROPS] });

    // when
    wrapper.vm.folderCreated(tv.FOLDER_PROPS_VARIANT);

    // then
    expect(wrapper.vm.folders).toEqual([
      tv.FOLDER_PROPS,
      tv.FOLDER_PROPS_VARIANT,
    ]);
    expect(wrapper.vm.folders[1]).toHaveProperty("highlightAnimation");
    expect(wrapper.vm.folders[1].highlightAnimation).toEqual(true);
  });
  it("folderMoved remove folder from list and deselect folder", () => {
    // given
    const folderToMove = tv.FOLDER_PROPS_VARIANT;
    const originalFoldersList = [tv.FOLDER_PROPS, folderToMove];
    const originalFoldersListLength = originalFoldersList.length;
    wrapper.setData({ folders: originalFoldersList });

    // when
    wrapper.vm.folderMoved({ folder: folderToMove });

    // then
    expect(wrapper.vm.folders.length).toBe(originalFoldersListLength - 1);
    expect(mockedUnselectFolder).toHaveBeenCalledTimes(1);
  });
  it("folderDeleted remove folder from list and deselect folder", () => {
    // given
    const folderToDelete = tv.FOLDER_PROPS_VARIANT;
    const originalFoldersList = [tv.FOLDER_PROPS, folderToDelete];
    const originalFoldersListLength = originalFoldersList.length;
    wrapper.setData({ folders: originalFoldersList });

    // when
    wrapper.vm.folderDeleted({ folder: folderToDelete });

    // then
    expect(wrapper.vm.folders.length).toBe(originalFoldersListLength - 1);
    expect(mockedUnselectFolder).toHaveBeenCalledTimes(1);
  });
  it("folderDeleted commit change to vue store if selected folder match deleted one", () => {
    // given selected folder does NOT match deleted one
    const folderToDelete = tv.FOLDER_PROPS_VARIANT;
    const originalFoldersList = [tv.FOLDER_PROPS, folderToDelete];
    wrapper.setData({ folders: originalFoldersList });

    // when
    wrapper.vm.folderDeleted({ folder: folderToDelete });

    // then
    expect(mockedSelectMoveTargetFolder).toBeCalledTimes(0);

    // given selected folder DOES match deleted one
    mockedFTLTreeItemSelected.mockReturnValue(true);
    wrapper.setData({ folders: originalFoldersList });

    // when
    wrapper.vm.folderDeleted({ folder: folderToDelete });

    // then
    expect(mockedSelectMoveTargetFolder).toBeCalledTimes(1);
    expect(mockedSelectMoveTargetFolder).toHaveBeenNthCalledWith(
      1,
      storeConfigCopy.state,
      null
    );
  });
  it("folderUpdated update folder in list", () => {
    // given
    const folderToUpdate = tv.FOLDER_PROPS_VARIANT;
    const originalFoldersList = [tv.FOLDER_PROPS, folderToUpdate];
    const originalFoldersListLength = originalFoldersList.length;
    wrapper.setData({ folders: originalFoldersList });

    // when
    const folderUpdated = Object.assign({}, folderToUpdate); // shallow copy
    const updatedName = "bingo!";
    folderUpdated.name = updatedName;
    wrapper.vm.folderUpdated({ folder: folderUpdated });

    // then
    expect(wrapper.vm.folders.length).toBe(originalFoldersListLength);
    expect(wrapper.vm.folders[1].name).not.toBe(folderToUpdate.name);
    expect(wrapper.vm.folders[1].name).toBe(updatedName);
  });
  it("folder watcher call proper methods", () => {
    // reset folder value
    wrapper.setData({ folder: null });
    mockedUpdateFoldersFromUrl.mockClear();

    const newFolder = tv.FOLDER_PROPS_VARIANT;
    //when a new folder is set
    wrapper.setData({ folder: newFolder });

    //then
    expect(mockedUpdateFoldersFromUrl).toHaveBeenCalledTimes(1);
    expect(mockedUpdateFoldersFromUrl).toHaveBeenCalledWith(newFolder);

    //when the same folder is set
    wrapper.setData({
      folder: newFolder,
      previousLevels: [tv.FOLDER_PROPS_VARIANT],
    });

    //then nothing new happens
    expect(mockedUpdateFoldersFromUrl).toHaveBeenCalledTimes(1);

    //when the folder is undefined
    wrapper.setData({ folder: undefined });

    //then
    expect(wrapper.vm.previousLevels).toEqual([]);
    expect(mockedUpdateFolders).toHaveBeenCalledTimes(1);
  });
});

describe("ManageFolders methods call api", () => {
  let wrapper;
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(ManageFolders, {
      localVue,
      methods: Object.assign(
        {
          unselectFolder: mockedUnselectFolder,
          refreshFolder: mockedRefreshFolder,
          navigateToFolder: mockedNavigateToFolder,
        },
        mountedMocks
      ),
      propsData: { folder },
      computed: {
        breadcrumb: mockedBreadcrumb,
        getCurrentFolder: mockedGetCurrentFolder,
      },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("getFolderDetail call api", async () => {
    axios.get.mockResolvedValue(mockedGetFolderDetailsResponse);

    // when
    wrapper.vm.getFolderDetail(folder);
    await flushPromises();

    // then
    expect(axios.get).toHaveBeenCalledWith("/app/api/v1/folders/" + folder.id);
    expect(axios.get).toHaveBeenCalledTimes(1);
  });
  it("updateFolders call api", async () => {
    // restore original method to test it
    wrapper.setMethods({ updateFolders: ManageFolders.methods.updateFolders });
    axios.get.mockResolvedValue(mockedGetFoldersListResponse);

    // when
    wrapper.vm.updateFolders();
    await flushPromises();

    // then
    expect(axios.get).toHaveBeenCalledWith("/app/api/v1/folders");
    expect(axios.get).toHaveBeenCalledTimes(1);

    // when called with folder arg
    jest.clearAllMocks();
    wrapper.vm.updateFolders(folder);
    await flushPromises();

    // then
    expect(axios.get).toHaveBeenCalledWith(
      "/app/api/v1/folders?level=" + folder.id
    );
    expect(axios.get).toHaveBeenCalledTimes(1);
  });
  it("updateFoldersFromUrl call api", async () => {
    axios.get.mockResolvedValue(mockedGetFolderDetailsResponse);
    wrapper.setMethods({
      updateFoldersFromUrl: ManageFolders.methods.updateFoldersFromUrl,
    });

    // when folder in url IS already the one selected
    wrapper.setData({ folderDetail: folder });
    wrapper.vm.updateFoldersFromUrl(folder.id);
    await flushPromises();

    // then no API call is made
    expect(axios.get).not.toHaveBeenCalled();

    // when folder in url is NOT already the one selected
    wrapper.vm.updateFoldersFromUrl(tv.FOLDER_PROPS_VARIANT.id);
    await flushPromises();

    // then API call is made
    expect(axios.get).toHaveBeenCalledTimes(1);
    expect(axios.get).toHaveBeenCalledWith(
      "/app/api/v1/folders/" + tv.FOLDER_PROPS_VARIANT.id
    );
  });
});

describe("ManageFolders methods error handling", () => {
  let wrapper;
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(ManageFolders, {
      localVue,
      methods: Object.assign(
        {
          unselectFolder: mockedUnselectFolder,
          refreshFolder: mockedRefreshFolder,
          navigateToFolder: mockedNavigateToFolder,
        },
        mountedMocks
      ),
      propsData: { folder },
      computed: {
        breadcrumb: mockedBreadcrumb,
        getCurrentFolder: mockedGetCurrentFolder,
      },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("getFolderDetail call mixinAlert in case of error", async () => {
    // force an error
    axios.get.mockRejectedValue("fakeError");

    // when
    wrapper.vm.getFolderDetail(folder);
    await flushPromises();

    // then mixinAlert is called with proper message
    expect(mockedMixinAlert).toHaveBeenCalledTimes(1);
    expect(mockedMixinAlert.mock.calls[0][0]).toContain("folder details");
  });
  it("updateFolders call mixinAlert in case of error", async () => {
    // restore original method to test it
    wrapper.setMethods({ updateFolders: ManageFolders.methods.updateFolders });
    // force an error
    axios.get.mockRejectedValue("fakeError");

    // when
    wrapper.vm.updateFolders();
    await flushPromises();

    // then mixinAlert is called with proper message
    expect(mockedMixinAlert).toHaveBeenCalledTimes(1);
    expect(mockedMixinAlert.mock.calls[0][0]).toContain("refresh folders");
  });
  it("updateFoldersFromUrl call mixinAlert in case of error", async () => {
    // restore original method to test it
    wrapper.setMethods({
      updateFoldersFromUrl: ManageFolders.methods.updateFoldersFromUrl,
    });
    // force an error
    axios.get.mockRejectedValue("fakeError");

    // when
    wrapper.vm.updateFoldersFromUrl();
    await flushPromises();

    // then mixinAlert is called with proper message
    expect(mockedMixinAlert).toHaveBeenCalledTimes(1);
    expect(mockedMixinAlert.mock.calls[0][0]).toContain("open folder");
  });
});

describe("Event received and handled by component", () => {
  let wrapper;
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(ManageFolders, {
      localVue,
      methods: Object.assign(
        {
          unselectFolder: mockedUnselectFolder,
          refreshFolder: mockedRefreshFolder,
          navigateToFolder: mockedNavigateToFolder,
          getFolderDetail: mockedGetFolderDetail,
          folderMoved: mockedFolderMoved,
          folderDeleted: mockedFolderDeleted,
          folderUpdated: mockedFolderUpdated,
          folderCreated: mockedFolderCreated,
        },
        mountedMocks
      ),
      propsData: { folder },
      computed: {
        breadcrumb: mockedBreadcrumb,
        getCurrentFolder: mockedGetCurrentFolder,
      },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("event-navigate-folder call navigateToFolder", async () => {
    // Need to defined some folders for FTLSelectableFolder to appears
    wrapper.setData({ folders: mockedGetFoldersListResponse.data });

    // when
    wrapper.find(FTLSelectableFolder).vm.$emit("event-navigate-folder", folder);
    await flushPromises();

    // then
    expect(mockedNavigateToFolder).toHaveBeenCalledTimes(1);
    expect(mockedNavigateToFolder).toHaveBeenCalledWith(folder);
  });
  it("event-select-folder call getFolderDetail", async () => {
    // Need to defined some folders for FTLSelectableFolder to appears
    wrapper.setData({ folders: mockedGetFoldersListResponse.data });

    // when
    wrapper.find(FTLSelectableFolder).vm.$emit("event-select-folder", folder);
    await flushPromises();

    // then
    expect(mockedGetFolderDetail).toHaveBeenCalledTimes(1);
    expect(mockedGetFolderDetail).toHaveBeenCalledWith(folder);
  });
  it("event-unselect-folder call unselectFolder", async () => {
    // Need to defined some folders for FTLSelectableFolder to appears
    wrapper.setData({ folders: mockedGetFoldersListResponse.data });

    // when
    wrapper.find(FTLSelectableFolder).vm.$emit("event-unselect-folder", folder);
    await flushPromises();

    // then
    expect(mockedUnselectFolder).toHaveBeenCalledTimes(1);
  });
  it("event-folder-renamed call folderUpdated", async () => {
    // Need to defined folderDetail for FTLRenameFolder to appears
    wrapper.setData({ folderDetail: folder });

    // when
    wrapper.find(FTLRenameFolder).vm.$emit("event-folder-renamed", folder);
    await flushPromises();

    // then
    expect(mockedFolderUpdated).toHaveBeenCalledTimes(1);
    expect(mockedFolderUpdated).toHaveBeenCalledWith(folder);
  });
  it("event-folder-created call folderCreated", async () => {
    // when
    wrapper.find(FTLNewFolder).vm.$emit("event-folder-created", folder);
    await flushPromises();

    // then
    expect(mockedFolderCreated).toHaveBeenCalledTimes(1);
    expect(mockedFolderCreated).toHaveBeenCalledWith(folder);
  });
  it("event-folder-deleted call folderDeleted", async () => {
    // Need to defined folderDetail for FTLRenameFolder to appears
    wrapper.setData({ folderDetail: folder });

    // when
    wrapper
      .find(FTLDeleteFolder)
      .vm.$emit("event-folder-deleted", { folder: folder });

    // then
    expect(mockedFolderDeleted).toHaveBeenCalledTimes(1);
    expect(mockedFolderDeleted).toHaveBeenCalledWith({ folder: folder });
  });
  it("event-folder-moved call folderMoved", async () => {
    // Need to defined folderDetail for FTLRenameFolder to appears
    wrapper.setData({ folderDetail: folder });

    // when
    wrapper.find(FTLMoveFolder).vm.$emit("event-folder-moved", {
      folder: folder,
      target_folder: targetFolder,
    });

    // then
    expect(mockedFolderMoved).toHaveBeenCalledTimes(1);
    expect(mockedFolderMoved).toHaveBeenCalledWith({
      folder: folder,
      target_folder: targetFolder,
    });
  });
});
