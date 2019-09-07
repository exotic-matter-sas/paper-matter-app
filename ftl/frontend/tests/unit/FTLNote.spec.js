import {createLocalVue, shallowMount} from '@vue/test-utils';

import axios from 'axios';
import BootstrapVue from "bootstrap-vue";
import flushPromises from "flush-promises"; // needed for async tests
import * as tv from './../tools/testValues.js'
import {axiosConfig} from "../../src/constants";

import FTLNote from "../../src/components/FTLNote";

// Create clean Vue instance and set installed package to avoid warning
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
  patch: jest.fn(),
}));

const mockedPatchDocument = {
  data: tv.DOCUMENT_PROPS,
  status: 200
};

const docProp = tv.DOCUMENT_PROPS;

describe('FTLNote template', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = shallowMount(FTLNote, {
      localVue,
      propsData: {doc: docProp}
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('renders properly FTLNote data', () => {
    expect(wrapper.html()).toContain(tv.DOCUMENT_PROPS.note);
  });
});

describe('FTLNote methods', () => {
  let wrapper;
  beforeEach(() => {
    axios.patch.mockResolvedValue(mockedPatchDocument);
    wrapper = shallowMount(FTLNote, {
      localVue,
      propsData: {doc: docProp}
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('updateNote call api', () => {
    wrapper.setData({text: "new note"});
    // when
    wrapper.vm.updateNote();

    // then
    expect(axios.patch).toHaveBeenCalledWith('/app/api/v1/documents/' + docProp.pid, {note: "new note"}, axiosConfig);
    expect(axios.patch).toHaveBeenCalledTimes(1);
  });

  it('updateNote emit event event-document-note-edited', async () => {
    const testedEvent = 'event-document-note-edited';

    // when
    wrapper.vm.updateNote();
    await flushPromises();

    // then
    expect(wrapper.emitted(testedEvent)).toBeTruthy();
    expect(wrapper.emitted(testedEvent).length).toBe(1);
    expect(wrapper.emitted(testedEvent)[0]).toEqual([{doc: mockedPatchDocument.data}])
  });

  it('updateNote call mixinAlert in case of API error', async () => {
    axios.patch.mockRejectedValue('errorDescription');

    // when
    wrapper.vm.updateNote();
    await flushPromises();

    // then
    expect(mockedMixinAlert).toHaveBeenCalledTimes(1);
    expect(mockedMixinAlert.mock.calls[0][0]).toContain('Could not save note!');
  });
});
