import {createLocalVue, shallowMount} from '@vue/test-utils';

import axios from 'axios';
import BootstrapVue from "bootstrap-vue";
import flushPromises from "flush-promises"; // needed for async tests

import * as tv from './../tools/testValues.js'
import {axiosConfig} from "../../src/constants";

import FTLDocument from "../../src/components/FTLDocument";

const localVue = createLocalVue();
// mock BootstrapVue Modal method, need to be before use BootstrapVue line
localVue.prototype.$bvModal = {msgBoxConfirm: jest.fn()};
localVue.use(BootstrapVue); // avoid bootstrap vue warnings

localVue.component('font-awesome-icon', jest.fn()); // avoid font awesome warnings

localVue.prototype.$_ = (text) => {return text}; // i18n mock
localVue.prototype.$moment = () => {return {fromNow: jest.fn()}}; // moment mock
const mockedMixinAlert = jest.fn();
localVue.mixin({methods: {mixinAlert: mockedMixinAlert}}); // mixinAlert mock

jest.mock('axios', () => ({
  delete: jest.fn()
}));

const mockedDeleteResponse = {
  data: {},
  status: 204,
  config: axiosConfig
};

describe('FTLDocument template', () => {
  const wrapper = shallowMount(FTLDocument, {
    localVue,
    propsData: {doc: tv.DOCUMENT_PROPS}
  });

  it('renders properly document data', () => {
    const ignoredProps = [tv.DOCUMENT_PROPS.note, tv.DOCUMENT_PROPS.thumbnail_available];

    Object.values(tv.DOCUMENT_PROPS)
      .filter((prop) => {
        // Filter out note and thumbnail_available because they are not shown in template
        return !ignoredProps.some((val) => {
          return val === prop;
        })
      })
      .forEach(function (documentData) {
        expect(wrapper.html()).toContain(documentData)
      });
  });
});

describe('FTLDocument script', () => {
  let wrapper;
  const testedDocument = tv.DOCUMENT_PROPS;

  beforeEach(() => {
    // given
    axios.delete.mockResolvedValue(mockedDeleteResponse);
    localVue.prototype.$bvModal.msgBoxConfirm.mockResolvedValue(true);
    wrapper = shallowMount(FTLDocument, {
      localVue,
      propsData: {doc: testedDocument}
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('openDocument emit event-open-doc', async () => {
    const testedEvent = 'event-open-doc';

    // when
    wrapper.vm.openDoc();
    await flushPromises();

    // then
    expect(wrapper.emitted(testedEvent)).toBeTruthy();
    expect(wrapper.emitted(testedEvent).length).toBe(1);
    expect(wrapper.emitted(testedEvent)[0]).toEqual([testedDocument.pid])
  });

  it('deleteDocument call api', async () => {
    // when
    wrapper.vm.deleteDocument();
    await flushPromises();

    // then
    expect(axios.delete).toHaveBeenCalledWith(
      '/app/api/v1/documents/' + testedDocument.pid,
      axiosConfig
    );
  });

  it('deleteDocument emit event-delete-doc', async () => {
    // when
    wrapper.vm.deleteDocument();
    await flushPromises();

    // then
    expect(wrapper.emitted('event-delete-doc')).toBeTruthy();
  });

  it('deleteDocument ask user for confirmation with $bvModal.msgBoxConfirm', async () => {
    // when
    wrapper.vm.deleteDocument();
    await flushPromises();

    // then
    expect(localVue.prototype.$bvModal.msgBoxConfirm).toHaveBeenCalledTimes(1);
    const modalFirstArg = localVue.prototype.$bvModal.msgBoxConfirm.mock.calls[0][0]
    expect(modalFirstArg).toContain('confirm');
    expect(modalFirstArg).toContain('delete');
    expect(modalFirstArg).toContain('document');
  });

  it('deleteDocument call mixinAlert in case of API error', async () => {
    // force an error
    axios.delete.mockRejectedValue('errorDescription');

    // when
    wrapper.vm.deleteDocument();
    await flushPromises();

    // then mixinAlert is called with proper message
    expect(mockedMixinAlert).toHaveBeenCalledTimes(1);
    const modalFirstArg = mockedMixinAlert.mock.calls[0][0];
    expect(modalFirstArg).toContain('delete');
    expect(modalFirstArg).toContain('document');
  });
});
