import {createLocalVue, shallowMount} from "@vue/test-utils";
import FTLThumbnailGenMixin from "@/components/FTLThumbnailGenMixin";
import BootstrapVue from "bootstrap-vue";
import axios from 'axios';
import {axiosConfig} from "../../src/constants";
import {createThumbFromUrl} from '../../src/thumbnailGenerator';
import * as tv from './../tools/testValues.js';
import flushPromises from "flush-promises"; // needed for async tests

const localVue = createLocalVue();
localVue.use(BootstrapVue); // to avoid warning on tests execution
localVue.component('font-awesome-icon', jest.fn()); // avoid font awesome warning
localVue.prototype.$_ = (text) => {
  return text;
}; // i18n mock
localVue.prototype.$moment = () => {
  return {fromNow: jest.fn()}
};
localVue.prototype.$router = {push: jest.fn()}; // router mock
const mockedMixinAlert = jest.fn();
localVue.mixin({methods: {mixinAlert: mockedMixinAlert}}); // mixin alert

jest.mock('../../src/thumbnailGenerator', () => ({
  __esModule: true,
  createThumbFromUrl: jest.fn()
}));

jest.mock('axios', () => ({
  get: jest.fn(),
  post: jest.fn(),
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
  data: Promise.resolve({
    count: 1,
    next: null,
    previous: "http://localhost/previous",
    results: [tv.DOCUMENT_NO_THUMB_PROPS_2]
  }),
  status: 200,
};

describe('FTLThumbnailGenMixin methods call proper api', () => {
  let wrapper;

  beforeEach(() => {
    wrapper = shallowMount(FTLThumbnailGenMixin, {
        localVue,
      }
    );
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('createThumbnailForDocument call api', async () => {
    axios.patch.mockResolvedValue({});

    createThumbFromUrl.mockResolvedValue("base64str");

    wrapper.vm.createThumbnailForDocument(tv.DOCUMENT_PROPS);
    await flushPromises();

    expect(axios.patch).toHaveBeenCalledWith(
      '/app/api/v1/documents/' + tv.DOCUMENT_PROPS.pid,
      {'thumbnail_binary': 'base64str'},
      axiosConfig
    );
    expect(axios.patch).toHaveBeenCalledTimes(1);
  });
});
