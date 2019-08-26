import {createLocalVue, shallowMount} from '@vue/test-utils';

import axios from 'axios';
import BootstrapVue from "bootstrap-vue";
import flushPromises from "flush-promises"; // needed for async tests
import * as tv from './../tools/testValues.js'
import {axiosConfig} from "../../src/constants";

import FTLRenameDocument from "../../src/components/FTLRenameDocument";

const localVue = createLocalVue();

// Mock BootstrapVue prototypes here (eg. localVue.prototype.$bvModal = {msgBoxConfirm: jest.fn()}; )
localVue.use(BootstrapVue); // avoid bootstrap vue warnings
localVue.component('font-awesome-icon', jest.fn()); // avoid font awesome warnings

// Mock prototype and mixin bellow
localVue.prototype.$_ = (text, args) => {
  return text + ' ' + args
};// i18n mock
localVue.prototype.$moment = () => {
  return {fromNow: jest.fn()}
}; // moment mock
localVue.prototype.$router = {push: jest.fn()}; // router mock
const mockedMixinAlert = jest.fn();
localVue.mixin({methods: {mixinAlert: mockedMixinAlert}}); // mixinAlert mock

// mock calls to api requests
jest.mock('axios', () => ({
  patch: jest.fn(),
}));

const mockedRenameDocumentResponse = {
  data: tv.DOCUMENT_PROPS,
  status: 200,
};

const documentProp = tv.DOCUMENT_PROPS;

describe('FTLRenameDocument template', () => {
  let wrapper;
  // defined const specific to this describe here
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(FTLRenameDocument, {
      localVue,
      propsData: {
        doc: documentProp
      }
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('renders properly component template', () => {
    expect(wrapper.text()).toContain('Rename document');
  });
});

describe('FTLRenameDocument methods', () => {
  let wrapper;
  // defined const specific to this describe here
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(FTLRenameDocument, {
      localVue,
      propsData: {
        doc: documentProp
      }
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('renameDocument call api', async () => {
    axios.patch.mockResolvedValue(mockedRenameDocumentResponse);
    // given
    const newDocumentName = 'renamed document';
    wrapper.setData({newDocumentName});

    // when
    wrapper.vm.renameDocument();
    await flushPromises();

    // then
    expect(axios.patch).toHaveBeenCalledWith(
      '/app/api/v1/documents/' + documentProp.pid,
      {title: newDocumentName},
      axiosConfig
    );
    expect(axios.patch).toHaveBeenCalledTimes(1);
    expect(mockedMixinAlert).toHaveBeenCalledTimes(1);
    expect(mockedMixinAlert.mock.calls[0][0]).toContain('successfully');
  });

  it('renameDocument call mixinAlert in case of error', async () => {
    // force an error
    axios.patch.mockRejectedValue('fakeError');

    // when
    wrapper.vm.renameDocument();
    await flushPromises();

    // then mixinAlert is called with proper message
    expect(mockedMixinAlert).toHaveBeenCalledTimes(1);
    expect(mockedMixinAlert.mock.calls[0][0]).toContain('Could not rename document');
  });

  it('event-document-renamed when calling renameDocument', async () => {
    axios.patch.mockResolvedValue(mockedRenameDocumentResponse);
    const testedEvent = 'event-document-renamed';

    // when
    wrapper.vm.renameDocument();
    await flushPromises();

    // then
    expect(wrapper.emitted(testedEvent)).toBeTruthy();
    expect(wrapper.emitted(testedEvent).length).toBe(1);
    expect(wrapper.emitted(testedEvent)[0]).toEqual([mockedRenameDocumentResponse.data]);
  });
});
