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
localVue.prototype.$_ = (text, args = '') => {
  return text + args
};// i18n mock
localVue.prototype.$moment = () => {
  return {fromNow: jest.fn()}
}; // moment mock
localVue.prototype.$router = {push: jest.fn()}; // router mock
const mockedMixinAlert = jest.fn();
localVue.mixin({methods: {mixinAlert: mockedMixinAlert}}); // mixinAlert mock
jest.mock('../../src/thumbnailGenerator', () => ({
  __esModule: true,
  createThumbFromUrl: jest.fn()
}));

jest.mock('axios', () => ({
  get: jest.fn(),
  patch: jest.fn()
}));

const mockedGetDocumentFlat1Response = {
  data: {
    count: 2,
    next: "http://localhost/next",
    previous: null,
    results: [tv.DOCUMENT_PROPS, tv.DOCUMENT_NO_THUMB_PROPS]
  },
  status: 200,
};
const mockedGetDocumentFlat2Response = {
  data: {
    count: 1,
    next: null,
    previous: "http://localhost/previous",
    results: [tv.DOCUMENT_NO_THUMB_PROPS_2]
  },
  status: 200,
};

const mockedCreateThumbnailForDocument = jest.fn();

describe('Component template', () => {
  let wrapper;
  beforeEach(() => {
    mockedCreateThumbnailForDocument.mockResolvedValue("DD");
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
    const elementSelector = '#generate-missing-thumbnails';
    const elem = wrapper.find(elementSelector);
    expect(elem.is(elementSelector)).toBe(true);
  });
});

describe('Konami methods', () => {
  let wrapper;
  beforeEach(() => {
    mockedCreateThumbnailForDocument.mockResolvedValue("DD");
    wrapper = shallowMount(Konami, {
      localVue,
      methods: {
        createThumbnailForDocument: mockedCreateThumbnailForDocument,
      },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('generateMissingThumbnail call api', async () => {
    axios.get.mockResolvedValueOnce(mockedGetDocumentFlat1Response);
    axios.get.mockResolvedValueOnce(mockedGetDocumentFlat2Response);

    wrapper.vm.generateMissingThumbnail();
    await flushPromises();

    expect(axios.get).toHaveBeenCalledWith("/app/api/v1/documents?flat=true");
    expect(axios.get).toHaveBeenCalledWith("http://localhost/next");
    // mocked API responses contains 2 documents without thumbs
    expect(axios.get).toHaveBeenCalledTimes(2);
  });

  it('generateMissingThumbnail call proper methods', async () => {
    axios.get.mockResolvedValueOnce(mockedGetDocumentFlat1Response);
    axios.get.mockResolvedValueOnce(mockedGetDocumentFlat2Response);

    wrapper.vm.generateMissingThumbnail();
    await flushPromises();

    // Only 2 thumbnails are not available in the 3 documents listed
    expect(mockedCreateThumbnailForDocument).toHaveBeenCalledTimes(2);
    expect(mockedMixinAlert).toBeCalledTimes(2 + 1); // 1 call for each of the 2 docs processed and 1 for processing finished
    const alertCalls = mockedMixinAlert.mock.calls;
    expect(alertCalls[alertCalls.length-1][0]).toContain('Finished');
  });

  it('generateMissingThumbnail call mixinAlert in case of API error', async () => {
    // force an API error
    axios.get.mockRejectedValue('fakeError');

    // when
    wrapper.vm.generateMissingThumbnail();
    await flushPromises();

    // then mixinAlert is called with proper message
    expect(mockedMixinAlert).toBeCalledTimes(1 + 1); // 1 call is always make at the end when process finished
    expect(mockedMixinAlert.mock.calls[0][0]).toContain('unknown error');
  });

  it('generateMissingThumbnail call mixinAlert in case of createThumbnailForDocument error', async () => {
    axios.get.mockResolvedValueOnce(mockedGetDocumentFlat2Response);
    // force an createThumbnailForDocument error
    mockedCreateThumbnailForDocument.mockRejectedValue("fakeError");

    // when
    wrapper.vm.generateMissingThumbnail();
    await flushPromises();

    // then mixinAlert is called with proper message
    expect(mockedMixinAlert).toBeCalledTimes(1 + 1);  // 1 call is always make at the end when process finished
    expect(mockedMixinAlert.mock.calls[0][0]).toContain('create thumbnail');
  });
});
