import {createLocalVue, shallowMount} from '@vue/test-utils';

import axios from 'axios';
import BootstrapVue from "bootstrap-vue";
import flushPromises from "flush-promises"; // needed for async tests

import * as tv from './../tools/testValues.js'
import {axiosConfig} from "../../src/constants";

import Home from "../../src/views/Home"; // TODO import tested component here
// TODO Import all needed Vue components here

// Create clean Vue instance and set installed package to avoid warning
const localVue = createLocalVue();
localVue.use(BootstrapVue); // avoid bootstrap vue warnings
localVue.component('font-awesome-icon', jest.fn()); // avoid font awesome warnings

// Mock prototype and mixin bellow
localVue.prototype.$_ = (text) => {return text}; // i18n mock
localVue.prototype.$moment = () => {return {fromNow: jest.fn()}}; // moment mock
localVue.prototype.$router = {push: jest.fn()}; // router mock
localVue.mixin({methods: {mixinAlert: jest.fn()}}); // mixin alert mock

// TODO mock thumbnail generation if needed (when test add documents)
import {createThumbFromUrl} from '../../src/thumbnailGenerator';
jest.mock('../../src/thumbnailGenerator', () => ({
  __esModule: true,
  createThumbFromUrl: jest.fn()
}));

// mock calls to api requests
jest.mock('axios', () => ({
  get: jest.fn(),
  // TODO add additional http word here if needed (post, patch...)
}));

// TODO store mocked response for tested api request here
const mockedGetRequestA = {
  data: tv.DOCUMENT_PROPS,
  status: 200,
  config: axiosConfig
};

// TODO mock tested component methods here
const mockedMethodA = jest.fn();
const mockedMethodB = jest.fn();
const mockedMethodC = jest.fn();

// TODO list method call in Component.mounted here
const mountedMocks = {
  methodB: mockedMethodB,
  methodC: mockedMethodC,
};

describe('Component first type of test', () => {

  beforeEach(() => {
    const wrapper = shallowMount(Home, {
      localVue,
      methods: mountedMocks
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('sync test', () => {
    // when method is called / event is emitted...
    // then expect something
  });

  it('async test', async () => {
    // when method is called / event is emitted...
    await flushPromises(); // wait all pending promises are resolves / rejected
    // then expect something
  });
});

// TODO add as many describe block as needed
