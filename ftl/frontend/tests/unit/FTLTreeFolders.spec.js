/*
 * Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
 * Licensed under the BSL License. See LICENSE in the project root for license information.
 */

import {createLocalVue, shallowMount} from '@vue/test-utils';

import axios from 'axios';
import BootstrapVue from "bootstrap-vue";
import flushPromises from "flush-promises"; // needed for async tests

import * as tv from './../tools/testValues.js'
import {axiosConfig} from "../../src/constants";

import FTLTreeFolders from "../../src/components/FTLTreeFolders";

const localVue = createLocalVue();

localVue.use(BootstrapVue); // avoid bootstrap vue warnings
localVue.component('font-awesome-icon', jest.fn()); // avoid font awesome warnings

localVue.prototype.$t = (text, args='') => {return text + args};// i18n mock
localVue.prototype.$tc = (text, args='') => {return text + args};// i18n mock
localVue.prototype.$moment = () => {return {fromNow: jest.fn()}}; // moment mock
localVue.prototype.$router = {push: jest.fn()}; // router mock
const mockedMixinAlert = jest.fn();
localVue.mixin({methods: {mixinAlert: mockedMixinAlert}}); // mixinAlert mock

// mock calls to api requests
jest.mock('axios', () => ({
  get: jest.fn(),
}));

const mockedGetFoldersListResponse = {
  data: [tv.FOLDER_PROPS, tv.FOLDER_PROPS_VARIANT],
  status: 200,
  config: axiosConfig
};

const folderToHide = 1;

describe('Component template', () => {
  let wrapper;
  beforeEach(() => {
    axios.get.mockResolvedValue(mockedGetFoldersListResponse);
    wrapper = shallowMount(FTLTreeFolders, {
      localVue,
      propsData: { folderToHide }
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('renders properly component template', () => {
    const elementSelector= '#moving-folders';
    const elem = wrapper.find(elementSelector);

    expect(elem.is(elementSelector)).toBe(true);
  });
});

describe('Component mounted without props', () => {
  let wrapper;
  beforeEach(() => {
    axios.get.mockClear();
    axios.get.mockResolvedValue(mockedGetFoldersListResponse);
    wrapper = shallowMount(FTLTreeFolders, {
      localVue,
      propsData: { folderToHide }
    });
  });

  it('mounted without props call api', async () => {
    // when mounted
    await flushPromises();

    // then
    expect(axios.get).toHaveBeenCalledWith('/app/api/v1/folders');
    expect(axios.get).toHaveBeenCalledTimes(1);
  });
});

describe('Component mounted with folderToHide props', () => {
  let wrapper;
  const folderToHide = tv.FOLDER_PROPS_VARIANT.id;
  beforeEach(() => {
    axios.get.mockResolvedValue(mockedGetFoldersListResponse);
    wrapper = shallowMount(FTLTreeFolders, {
      localVue,
      propsData: { folderToHide }
    });
  });

  it('folderToHide is filtered out from the GetFoldersListResponse', async () => {
    // when mounted
    await flushPromises();

    // then
    wrapper.vm.folders.forEach(function(folder){
      expect(folder.id).not.toBe(folderToHide);
    });
  });
});

describe('Component API error handling', () => {
  let wrapper;
  beforeEach(() => {
    axios.get.mockRejectedValue('fakeError');
    wrapper = shallowMount(FTLTreeFolders, {
      localVue,
      propsData: { folderToHide }
    });
  });

  it('mounted call mixinAlert in case of API error', async () => {
    // when mounted
    await flushPromises();

    // then mixinAlert is called with proper message
    expect(wrapper.vm.lastFolderListingFailed).toBe(true);
  });
});
