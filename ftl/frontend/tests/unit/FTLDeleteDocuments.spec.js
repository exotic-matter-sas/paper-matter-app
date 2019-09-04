import {createLocalVue, shallowMount} from '@vue/test-utils';
import FTLDeleteDocuments from "@/components/FTLDeleteDocuments";
import BootstrapVue from "bootstrap-vue";
import * as tv from "../tools/testValues";
import axios from "axios";
import {axiosConfig} from "@/constants";

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
const mockedMixinAlert = jest.fn();
localVue.mixin({methods: {mixinAlert: mockedMixinAlert}}); // mixinAlert mock

// mock calls to api requests
jest.mock('axios', () => ({
  delete: jest.fn(),
}));

const docsProp = [tv.DOCUMENT_PROPS, tv.DOCUMENT_PROPS_WITH_FOLDER];
const mockedDeletedDocument = {
  status: 204
};

describe('FTLDeleteDocuments template', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = shallowMount(FTLDeleteDocuments, {
      localVue,
      propsData: {docs: docsProp}
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('renders properly FTLDeleteDocuments data', () => {
    expect(wrapper.html()).toContain('Delete documents');
  });
});

describe('FTLDeleteDocuments methods', () => {
  let wrapper;
  beforeEach(() => {
    axios.delete.mockResolvedValue(mockedDeletedDocument);
    wrapper = shallowMount(FTLDeleteDocuments, {
      localVue,
      propsData: {docs: docsProp}
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('deleteDocuments call api', () => {
    // when
    wrapper.vm.deleteDocuments();

    // then
    expect(axios.delete).toHaveBeenCalledWith('/app/api/v1/documents/' + docsProp[0].pid, axiosConfig);
    expect(axios.delete).toHaveBeenCalledWith('/app/api/v1/documents/' + docsProp[1].pid, axiosConfig);
    expect(axios.delete).toHaveBeenCalledTimes(2);
  });
});
