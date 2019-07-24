import {createLocalVue, shallowMount} from '@vue/test-utils';

import axios from 'axios';
import BootstrapVue from "bootstrap-vue";
import flushPromises from "flush-promises"; // needed for async tests
import * as tv from './../tools/testValues.js'
import {axiosConfig} from "../../src/constants";

import FTLNewFolder from "../../src/components/FTLNewFolder";

const localVue = createLocalVue();

localVue.use(BootstrapVue); // avoid bootstrap vue warnings
localVue.component('font-awesome-icon', jest.fn()); // avoid font awesome warnings

localVue.prototype.$_ = (text) => {
  return text
}; // i18n mock
localVue.prototype.$moment = () => {
  return {fromNow: jest.fn()}
}; // moment mock
localVue.prototype.$router = {push: jest.fn()}; // router mock
const mockedMixinAlert = jest.fn();
localVue.mixin({methods: {mixinAlert: mockedMixinAlert}}); // mixinAlert mock


jest.mock('axios', () => ({
  post: jest.fn()
}));

const mockedPostFolderResponse = {
  data: tv.FOLDER_PROPS,
  status: 200,
  config: axiosConfig
};


describe('FTLNewFolder template', () => {
  let wrapper;

  beforeEach(() => {
    wrapper = shallowMount(FTLNewFolder, {
      localVue,
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('renders properly FTLNewFolder at Root level', async () => {
    await flushPromises();

    // then
    expect(wrapper.text()).toContain('Create');
    expect(wrapper.text()).toContain('folder');
  });
});

describe('createNewFolder scripts', () => {
  let wrapper;
  const currentFolder = tv.FOLDER_PROPS_VARIANT;

  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(FTLNewFolder, {
      localVue,
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('createNewFolder call api', async () => {
    axios.post.mockResolvedValue(mockedPostFolderResponse);
    wrapper.setData({newFolderName: tv.FOLDER_PROPS.name});

    // when
    wrapper.vm.createNewFolder();
    await flushPromises();

    // then
    expect(axios.post).toHaveBeenCalledWith(
      '/app/api/v1/folders/',
      {name: tv.FOLDER_PROPS.name},
      axiosConfig
    );
    expect(axios.post).toHaveBeenCalledTimes(1);
  });

  it('event-folder-created emitted when calling createNewFolder', async () => {
    const testedEvent = 'event-folder-created';
    axios.post.mockResolvedValue(mockedPostFolderResponse);
    wrapper.setData({newFolderName: tv.FOLDER_PROPS.name});

    // when
    wrapper.vm.createNewFolder();
    await flushPromises();

    // then
    expect(wrapper.emitted(testedEvent)).toBeTruthy();
    expect(wrapper.emitted(testedEvent).length).toBe(1);
    expect(wrapper.emitted(testedEvent)[0]).toEqual([mockedPostFolderResponse.data]);
  });

  it('createNewFolder call mixinAlert in case of error', async () => {
    // force an error
    axios.post.mockRejectedValue({response: {data: {'code': '', 'details': ''}}});

    // when
    wrapper.vm.createNewFolder();
    await flushPromises();

    // then mixinAlert is called with proper message
    expect(mockedMixinAlert).toHaveBeenCalledTimes(1);
    expect(mockedMixinAlert.mock.calls[0][0]).toContain('create new folder');
  });

  it('getParentName return proper value', () => {
    // when parent props unset
    let testedValue = wrapper.vm.getParentName;

    // then
    expect(testedValue).toBe('Root');

    // when parent props set
    wrapper.setProps({parent: currentFolder});
    testedValue = wrapper.vm.getParentName;

    // then
    expect(testedValue).toBe(currentFolder.name);
  });
});
