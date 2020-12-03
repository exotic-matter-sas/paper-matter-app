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

import FTLTreeItem from "@/components/FTLTreeItem";
import Vuex from "vuex";
import storeConfig from "@/store/storeConfig";
import cloneDeep from "lodash.clonedeep";

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
localVue.prototype.$router = { push: jest.fn() }; // router mock
const mockedMixinAlert = jest.fn();
localVue.mixin({ methods: { mixinAlert: mockedMixinAlert } }); // mixinAlert mock

jest.mock("axios", () => ({
  get: jest.fn(),
}));

const mockedGetFoldersListResponse = {
  data: [tv.FOLDER_PROPS, tv.FOLDER_PROPS_VARIANT],
  status: 200,
  config: axiosConfig,
};

const mockedListItemChildren = jest.fn();
const mockedSelected = jest.fn();
const mockedSelectMoveTargetFolder = jest.fn();
const mockedFTLTreeItemSelected = jest.fn();

const item = tv.FOLDER_TREE_ITEM;
const itemWithDescendant = tv.FOLDER_TREE_ITEM_WITH_DESCENDANT;
const folderToHide = 1;

describe("FTLTreeItem template", () => {
  let wrapper;
  let storeConfigCopy;
  let store;

  beforeEach(() => {
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(storeConfigCopy);
    wrapper = shallowMount(FTLTreeItem, {
      localVue,
      store,
      computed: {
        selected: mockedSelected,
      },
      propsData: { item, folderToHide },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("renders properly FTLTreeItem template", () => {
    const elementSelector = ".folder-tree-item";
    const elem = wrapper.find(elementSelector);

    expect(elem.is(elementSelector)).toBe(true);
    expect(wrapper.text()).toContain(tv.FOLDER_PROPS.name);
  });
});

describe("FTLTreeItem methods call proper methods", () => {
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
    wrapper = shallowMount(FTLTreeItem, {
      localVue,
      store,
      computed: {
        selected: mockedSelected,
      },
      methods: {
        listItemChildren: mockedListItemChildren,
      },
      propsData: { item: itemWithDescendant, folderToHide },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("toggle call proper methods", () => {
    //when calling toggle for the first time
    wrapper.vm.toggle();

    //then
    expect(wrapper.vm.isOpen).toBe(true);
    expect(mockedListItemChildren).toHaveBeenCalledTimes(1);
    expect(mockedListItemChildren).toHaveBeenCalledWith(item.id);

    //when calling toggle for the second time
    wrapper.vm.toggle();

    //then
    expect(wrapper.vm.isOpen).toBe(false);
    expect(wrapper.vm.item.children).toEqual([]);
    expect(mockedListItemChildren).toHaveBeenCalledTimes(1);
  });
  it("selectFolder commit to Vuex store", () => {
    // when
    wrapper.vm.selectFolder();

    // then
    expect(mockedSelectMoveTargetFolder).toBeCalledTimes(1);
    expect(mockedSelectMoveTargetFolder).toHaveBeenNthCalledWith(
      1,
      storeConfigCopy.state,
      { id: itemWithDescendant.id, name: itemWithDescendant.name }
    );

    // when
    mockedFTLTreeItemSelected.mockReturnValue(true);
    wrapper.vm.selectFolder();

    // then
    expect(mockedSelectMoveTargetFolder).toBeCalledTimes(2);
    expect(mockedSelectMoveTargetFolder).toHaveBeenNthCalledWith(
      2,
      storeConfigCopy.state,
      null
    );
  });
});

describe("FTLTreeItem methods call api", () => {
  let wrapper;
  let storeConfigCopy;
  let store;
  beforeEach(() => {
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(storeConfigCopy);
    wrapper = shallowMount(FTLTreeItem, {
      localVue,
      store,
      computed: {
        selected: mockedSelected,
      },
      propsData: { item, folderToHide },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("listItemChildren call api", async () => {
    axios.get.mockResolvedValue(mockedGetFoldersListResponse);
    const level = "level";

    // when
    wrapper.vm.listItemChildren(level);
    await flushPromises();

    // then
    expect(axios.get).toHaveBeenCalledWith(
      "/app/api/v1/folders?level=" + level
    );
    expect(axios.get).toHaveBeenCalledTimes(1);
  });

  it("listItemChildren filter api response based on folderToHide", async () => {
    axios.get.mockResolvedValue(mockedGetFoldersListResponse);
    const level = "level";
    const newFolderToHide = tv.FOLDER_PROPS_VARIANT.id;
    wrapper.setProps({ folderToHide: newFolderToHide });

    // when
    wrapper.vm.listItemChildren(level);
    await flushPromises();

    // then
    wrapper.vm.item.children.forEach(function (folder) {
      expect(folder.id).not.toBe(newFolderToHide);
    });
  });
});

describe("FTLTreeItem methods error handling", () => {
  let wrapper;
  let storeConfigCopy;
  let store;
  beforeEach(() => {
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(storeConfigCopy);
    wrapper = shallowMount(FTLTreeItem, {
      localVue,
      store,
      computed: {
        selected: mockedSelected,
      },
      propsData: { item, folderToHide },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("listItemChildren set lastFolderListingFailed in case of error", async () => {
    // force an error
    axios.get.mockRejectedValue("fakeError");

    // when
    wrapper.vm.listItemChildren();
    await flushPromises();

    // then mixinAlert is called with proper message
    expect(wrapper.vm.lastFolderListingFailed).toBe(true);
  });
});
