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

localVue.prototype.$_ = (text, args='') => {return text + args};// i18n mock
localVue.prototype.$moment = () => {return {fromNow: jest.fn()}}; // moment mock
localVue.prototype.$router = {push: jest.fn()}; // router mock
const mockedMixinAlert = jest.fn();
localVue.mixin({methods: {mixinAlert: mockedMixinAlert}}); // mixinAlert mock

// mock calls to api requests
jest.mock('axios', () => ({
  get: jest.fn(),
}));

// TODO store mocked response for tested api request here
const mockedGetFoldersListResponse = {
  data: [tv.FOLDER_PROPS, tv.FOLDER_PROPS_VARIANT],
  status: 200,
  config: axiosConfig
};

describe('Component template', () => {
  let wrapper;
  beforeEach(() => {
    axios.get.mockResolvedValue(mockedGetFoldersListResponse);
    wrapper = shallowMount(FTLTreeFolders, {
      localVue,
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('renders properly component template', () => {
    expect(wrapper.html()).toContain('id="moving-folders"');
  });
});

describe('Component mounted without props', () => {
  let wrapper;
  beforeEach(() => {
    axios.get.mockClear();
    axios.get.mockResolvedValue(mockedGetFoldersListResponse);
    wrapper = shallowMount(FTLTreeFolders, {
      localVue,
    });
  });

  it('mounted without props call api', async () => {
    // when mounted
    await flushPromises();

    // then
    expect(axios.get).toHaveBeenCalledWith('/app/api/v1/folders/');
    expect(axios.get).toHaveBeenCalledTimes(1);
  });
});

describe('Component mounted with start props', () => {
  let wrapper;
  const start = 4242;
  beforeEach(() => {
    axios.get.mockClear();
    axios.get.mockResolvedValue(mockedGetFoldersListResponse);
    wrapper = shallowMount(FTLTreeFolders, {
      localVue,
      propsData: { start }
    });
  });

  it('mounted with start props call api', async () => {
    // when mounted
    await flushPromises();

    // then
    expect(axios.get).toHaveBeenCalledWith('/app/api/v1/folders/?level=' + start);
    expect(axios.get).toHaveBeenCalledTimes(1);
  });
});

describe('Component mounted with root props false', () => {
  let wrapper;
  const root = false;
  beforeEach(() => {
    axios.get.mockResolvedValue(mockedGetFoldersListResponse);
    wrapper = shallowMount(FTLTreeFolders, {
      localVue,
      propsData: { root }
    });
  });

  it('mounted root props append data to folders data', async () => {
    // when mounted
    await flushPromises();

    // then
    expect(wrapper.vm.folders).toContainEqual({id: null, name: 'Root'});
  });
});

describe('Component mounted with sourceFolder props', () => {
  let wrapper;
  const sourceFolder = tv.FOLDER_PROPS_VARIANT.id;
  beforeEach(() => {
    axios.get.mockResolvedValue(mockedGetFoldersListResponse);
    wrapper = shallowMount(FTLTreeFolders, {
      localVue,
      propsData: { sourceFolder }
    });
  });

  it('sourceFolder is filtered out from the GetFoldersListResponse', async () => {
    // when mounted
    await flushPromises();

    // then
    wrapper.vm.folders.forEach(function(folder){
      expect(folder.id).not.toBe(sourceFolder);
    });
  });
});

describe('Component API error handling', () => {
  let wrapper;
  beforeEach(() => {
    axios.get.mockRejectedValue('fakeError');
    wrapper = shallowMount(FTLTreeFolders, {
      localVue,
    });
  });

  it('mounted call mixinAlert in case of API error', async () => {
    // when mounted
    await flushPromises();

    // then mixinAlert is called with proper message
    expect(mockedMixinAlert).toHaveBeenCalledTimes(1);
    expect(mockedMixinAlert.mock.calls[0][0]).toContain('refresh folders');
  });
});
