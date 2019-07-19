import {createLocalVue, shallowMount} from '@vue/test-utils';

import axios from 'axios';
import BootstrapVue from "bootstrap-vue";
import flushPromises from "flush-promises"; // needed for async tests

import * as tv from './../tools/testValues.js'
import {axiosConfig} from "../../src/constants";

import Konami from "../../src/views/Konami";

const localVue = createLocalVue();

localVue.use(BootstrapVue); // avoid bootstrap vue warnings
localVue.component('font-awesome-icon', jest.fn()); // avoid font awesome warnings

// Mock prototype and mixin bellow
localVue.prototype.$_ = (text, args='') => {return text + args};// i18n mock
localVue.prototype.$moment = () => {return {fromNow: jest.fn()}}; // moment mock
localVue.prototype.$router = {push: jest.fn()}; // router mock
const mockedMixinAlert = jest.fn();
localVue.mixin({methods: {mixinAlert: mockedMixinAlert}}); // mixinAlert mock

import {createThumbFromUrl} from '../../src/thumbnailGenerator';
jest.mock('../../src/thumbnailGenerator', () => ({
  __esModule: true,
  createThumbFromUrl: jest.fn()
}));

jest.mock('axios', () => ({
  get: jest.fn(),
  patch: jest.fn()
}));

const mockedGetDocumentsFlatResponse = {
  data: tv.DOCUMENT_PROPS,
  status: 200,
  config: axiosConfig
};
const mockedUpdateDocumentResponse = {
  data: tv.DOCUMENT_PROPS,
  status: 200,
  config: axiosConfig
};

const mockedCreateThumbnailForDocument = jest.fn();

describe('Component template', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = shallowMount(Konami, {
      localVue,
      methods: {
          createThumbnailForDocument: mockedCreateThumbnailForDocument,
      },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('renders properly text', () => {
    expect(wrapper.text().replace(/\s+/g, ' ')).toContain('Generate missing thumbnail');
  });
  it('renders properly html element', () => {
    const elementSelector= '#generate-missing-thumbnails';
    const elem = wrapper.find(elementSelector);
    expect(elem.is(elementSelector)).toBe(true);
  });
});
