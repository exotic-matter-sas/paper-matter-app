/*
 * Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
 * Licensed under the Business Source License. See LICENSE at project root for more information.
 */

import { createLocalVue, shallowMount } from "@vue/test-utils";

import axios from "axios";
import BootstrapVue from "bootstrap-vue";
import flushPromises from "flush-promises"; // needed for async tests
import * as tv from "./../tools/testValues.js";
import { axiosConfig } from "../../src/constants";

import FTLManageFoldersPanel from "../../src/components/FTLManageFoldersPanel";
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

global.window.matchMedia = jest.fn().mockReturnValue({ matches: jest.fn() });
global.document.querySelector = jest
  .fn()
  .mockReturnValue({ scrollIntoView: jest.fn() });

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
const mockedGetFolderDetails = jest.fn();
const mockedUnselectFolder = jest.fn();
const mockedNavigateToFolder = jest.fn();
const mockedBreadcrumb = jest.fn();
const mockedGetCurrentFolder = jest.fn();
const mockedFolderMoved = jest.fn();
const mockedFolderDeleted = jest.fn();
const mockedFolderUpdated = jest.fn();
const mockedFolderCreated = jest.fn();
const mockedFTLTreeItemSelected = jest.fn();
const mockedSelectMoveTargetFolder = jest.fn();
const mockedPreviousLevels = jest.fn();

const folder = tv.FOLDER_PROPS;
const targetFolder = tv.FOLDER_PROPS_VARIANT;

describe("FTLManageFoldersPanel template", () => {
  let wrapper;
  // defined const specific to this describe here
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(FTLManageFoldersPanel, {
      localVue,
      computed: {
        previousLevels: mockedPreviousLevels,
        getCurrentFolder: mockedGetCurrentFolder,
      },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("renders properly component template", () => {
    expect(wrapper.text()).toContain("No folder selected");
  });
});

describe("FTLManageFoldersPanel methods", () => {
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
    wrapper = shallowMount(FTLManageFoldersPanel, {
      localVue,
      store,
      methods: {
        unselectFolder: mockedUnselectFolder,
        refreshFolder: mockedRefreshFolder,
        navigateToFolder: mockedNavigateToFolder,
      },
      propsData: { folder },
      computed: {
        breadcrumb: mockedBreadcrumb,
        getCurrentFolder: mockedGetCurrentFolder,
      },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("unselectFolder update data", () => {
    // restore original method to test it
    wrapper.setMethods({
      unselectFolder: FTLManageFoldersPanel.methods.unselectFolder,
    });

    //when
    wrapper.setData({ folderDetail: tv.FOLDER_PROPS });
    wrapper.vm.unselectFolder();

    //then
    expect(wrapper.vm.folderDetail).toBe(null);
  });
  it("folderCreated add folder to the list, set folder.highlightAnimation + sync with home folders", () => {
    // given
    const testedEvent = "update:childrenFolders";
    wrapper.setData({ childrenFolders: [tv.FOLDER_PROPS] });

    // when
    wrapper.vm.folderCreated(tv.FOLDER_PROPS_VARIANT);

    // then
    expect(wrapper.vm.childrenFolders).toEqual([
      tv.FOLDER_PROPS_VARIANT,
      tv.FOLDER_PROPS,
    ]);
    expect(wrapper.vm.childrenFolders[0]).toHaveProperty("highlightAnimation");
    expect(wrapper.vm.childrenFolders[0].highlightAnimation).toEqual(true);

    expect(wrapper.emitted(testedEvent)).toBeTruthy();
    expect(wrapper.emitted(testedEvent).length).toBe(1);
    expect(wrapper.emitted(testedEvent)[0]).toEqual([
      wrapper.vm.childrenFolders,
    ]);
  });
  it("folderMoved remove folder from list and deselect folder + sync with home folders", () => {
    // given
    const testedEvent = "update:childrenFolders";
    const folderToMove = tv.FOLDER_PROPS_VARIANT;
    const originalFoldersList = [tv.FOLDER_PROPS, folderToMove];
    const originalFoldersListLength = originalFoldersList.length;
    wrapper.setData({ childrenFolders: originalFoldersList });

    // when
    wrapper.vm.folderMoved({ folder: folderToMove });

    // then
    expect(wrapper.vm.childrenFolders.length).toBe(
      originalFoldersListLength - 1
    );
    expect(mockedUnselectFolder).toHaveBeenCalledTimes(1);

    expect(wrapper.emitted(testedEvent)).toBeTruthy();
    expect(wrapper.emitted(testedEvent).length).toBe(1);
    expect(wrapper.emitted(testedEvent)[0]).toEqual([
      wrapper.vm.childrenFolders,
    ]);
  });
  it("folderDeleted remove folder from list and deselect folder + sync with home folders", () => {
    // given
    const testedEvent = "update:childrenFolders";
    const folderToDelete = tv.FOLDER_PROPS_VARIANT;
    const originalFoldersList = [tv.FOLDER_PROPS, folderToDelete];
    const originalFoldersListLength = originalFoldersList.length;
    wrapper.setData({ childrenFolders: originalFoldersList });

    // when
    wrapper.vm.folderDeleted({ folder: folderToDelete });

    // then
    expect(wrapper.vm.childrenFolders.length).toBe(
      originalFoldersListLength - 1
    );
    expect(mockedUnselectFolder).toHaveBeenCalledTimes(1);

    expect(wrapper.emitted(testedEvent)).toBeTruthy();
    expect(wrapper.emitted(testedEvent).length).toBe(1);
    expect(wrapper.emitted(testedEvent)[0]).toEqual([
      wrapper.vm.childrenFolders,
    ]);
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
    wrapper.setData({ childrenFolders: originalFoldersList });

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
    const testedEvent = "update:childrenFolders";
    const folderToUpdate = tv.FOLDER_PROPS_VARIANT;
    const originalFoldersList = [tv.FOLDER_PROPS, folderToUpdate];
    const originalFoldersListLength = originalFoldersList.length;
    wrapper.setData({ childrenFolders: originalFoldersList });

    // when
    const folderUpdated = Object.assign({}, folderToUpdate); // shallow copy
    const updatedName = "bingo!";
    folderUpdated.name = updatedName;
    wrapper.vm.folderUpdated({ folder: folderUpdated });

    // then
    expect(wrapper.vm.childrenFolders.length).toBe(originalFoldersListLength);
    expect(wrapper.vm.childrenFolders[1].name).not.toBe(folderToUpdate.name);
    expect(wrapper.vm.childrenFolders[1].name).toBe(updatedName);

    expect(wrapper.emitted(testedEvent)).toBeTruthy();
    expect(wrapper.emitted(testedEvent).length).toBe(1);
    expect(wrapper.emitted(testedEvent)[0]).toEqual([
      wrapper.vm.childrenFolders,
    ]);
  });
});

describe("FTLManageFoldersPanel methods call api", () => {
  let wrapper;
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(FTLManageFoldersPanel, {
      localVue,
      methods: {
        unselectFolder: mockedUnselectFolder,
        refreshFolder: mockedRefreshFolder,
        navigateToFolder: mockedNavigateToFolder,
      },
      propsData: { folder },
      computed: {
        breadcrumb: mockedBreadcrumb,
        getCurrentFolder: mockedGetCurrentFolder,
      },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("getFolderDetails call api", async () => {
    axios.get.mockResolvedValue(mockedGetFolderDetailsResponse);

    // when
    wrapper.vm.getFolderDetails(folder);
    await flushPromises();

    // then
    expect(axios.get).toHaveBeenCalledWith("/app/api/v1/folders/" + folder.id);
    expect(axios.get).toHaveBeenCalledTimes(1);
  });
});

describe("FTLManageFoldersPanel methods error handling", () => {
  let wrapper;
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(FTLManageFoldersPanel, {
      localVue,
      methods: {
        unselectFolder: mockedUnselectFolder,
        refreshFolder: mockedRefreshFolder,
        navigateToFolder: mockedNavigateToFolder,
      },
      propsData: { folder },
      computed: {
        breadcrumb: mockedBreadcrumb,
        getCurrentFolder: mockedGetCurrentFolder,
      },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("getFolderDetails call mixinAlert in case of error", async () => {
    // force an error
    axios.get.mockRejectedValue("fakeError");

    // when
    wrapper.vm.getFolderDetails(folder);
    await flushPromises();

    // then mixinAlert is called with proper message
    expect(mockedMixinAlert).toHaveBeenCalledTimes(1);
    expect(mockedMixinAlert.mock.calls[0][0]).toContain("folder details");
  });
});

describe("Event received and handled by component", () => {
  let wrapper;
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(FTLManageFoldersPanel, {
      localVue,
      methods: {
        unselectFolder: mockedUnselectFolder,
        refreshFolder: mockedRefreshFolder,
        navigateToFolder: mockedNavigateToFolder,
        getFolderDetails: mockedGetFolderDetails,
        folderMoved: mockedFolderMoved,
        folderDeleted: mockedFolderDeleted,
        folderUpdated: mockedFolderUpdated,
        folderCreated: mockedFolderCreated,
      },
      propsData: { folder },
      computed: {
        breadcrumb: mockedBreadcrumb,
        getCurrentFolder: mockedGetCurrentFolder,
      },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("event-select-folder call getFolderDetails", async () => {
    // Need to defined some folders for FTLSelectableFolder to appears
    wrapper.setData({ childrenFolders: mockedGetFoldersListResponse.data });

    // when
    wrapper.find(FTLSelectableFolder).vm.$emit("event-select-folder", folder);
    await flushPromises();

    // then
    expect(mockedGetFolderDetails).toHaveBeenCalledTimes(1);
    expect(mockedGetFolderDetails).toHaveBeenCalledWith(folder);
  });
  it("event-unselect-folder call unselectFolder", async () => {
    // Need to defined some folders for FTLSelectableFolder to appears
    wrapper.setData({ childrenFolders: mockedGetFoldersListResponse.data });

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
