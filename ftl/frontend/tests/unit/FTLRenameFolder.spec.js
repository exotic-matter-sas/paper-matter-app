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

import FTLRenameFolder from "../../src/components/FTLRenameFolder";

const localVue = createLocalVue();

// Mock BootstrapVue prototypes here (eg. localVue.prototype.$bvModal = {msgBoxConfirm: jest.fn()}; )
localVue.use(BootstrapVue); // avoid bootstrap vue warnings
localVue.component('font-awesome-icon', jest.fn()); // avoid font awesome warnings

// Mock prototype and mixin bellow
localVue.prototype.$_ = (text, args) => {return text + ' ' + args};// i18n mock
localVue.prototype.$moment = () => {return {fromNow: jest.fn()}}; // moment mock
localVue.prototype.$router = {push: jest.fn()}; // router mock
const mockedMixinAlert = jest.fn();
localVue.mixin({methods: {mixinAlert: mockedMixinAlert}}); // mixinAlert mock

// mock calls to api requests
jest.mock('axios', () => ({
  patch: jest.fn(),
}));

const mockedRenameFolderResponse = {
  data: tv.FOLDER_PROPS_WITH_PARENT,
  status: 200,
};

const folderProps = tv.FOLDER_PROPS;

describe('FTLRenameFolder template', () => {
  let wrapper;
  // defined const specific to this describe here
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(FTLRenameFolder, {
      localVue,
      propsData: {
        folder: folderProps
      }
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('renders properly component template', () => {
    expect(wrapper.text()).toContain('Rename folder');
  });
});

describe('FTLRenameFolder methods', () => {
  let wrapper;
  // defined const specific to this describe here
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(FTLRenameFolder, {
      localVue,
      propsData: {
        folder: folderProps
      }
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('renameFolder call api', async () => {
    axios.patch.mockResolvedValue(mockedRenameFolderResponse);
    // given
    const newFolderName = 'renamed Folder';
    wrapper.setData({ newFolderName });

    // when
    wrapper.vm.renameFolder();
    await flushPromises();

    // then
    expect(axios.patch).toHaveBeenCalledWith(
      '/app/api/v1/folders/'+ folderProps.id,
      {name: newFolderName},
      axiosConfig
      );
    expect(axios.patch).toHaveBeenCalledTimes(1);
    expect(mockedMixinAlert).toHaveBeenCalledTimes(1);
    expect(mockedMixinAlert.mock.calls[0][0]).toContain('success');
  });

  it('renameFolder call mixinAlert in case of error', async () => {
    // force an error
    axios.patch.mockRejectedValue('fakeError');

    // when
    wrapper.vm.renameFolder();
    await flushPromises();

    // then mixinAlert is called with proper message
    expect(mockedMixinAlert).toHaveBeenCalledTimes(1);
    expect(mockedMixinAlert.mock.calls[0][0]).toContain('rename folder');
  });

  it('event-folder-renamed emit when calling renameFolder', async () => {
    axios.patch.mockResolvedValue(mockedRenameFolderResponse);
    const testedEvent = 'event-folder-renamed';

    // when
    wrapper.vm.renameFolder();
    await flushPromises();

    // then
    expect(wrapper.emitted(testedEvent)).toBeTruthy();
    expect(wrapper.emitted(testedEvent).length).toBe(1);
    expect(wrapper.emitted(testedEvent)[0]).toEqual([{folder: mockedRenameFolderResponse.data}]);
  });
});
