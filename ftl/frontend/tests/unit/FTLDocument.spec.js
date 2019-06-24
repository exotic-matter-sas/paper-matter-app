import {createLocalVue, shallowMount} from '@vue/test-utils';

import axios from 'axios';

import * as tv from './../tools/testValues.js'
import FTLDocument from "../../src/components/FTLDocument";
import {axiosConfig} from "../../src/constants";
import flushPromises from "flush-promises";

const localVue = createLocalVue();
// to avoid warning on tests execution, commented out here because we need to mock bvModal
// localVue.use(BootstrapVue);
localVue.component('font-awesome-icon', jest.fn()); // avoid font awesome warning
localVue.prototype.$_ = (text) => {
  return text;
}; // i18n mock
localVue.prototype.$moment = () => {
  return {fromNow: jest.fn()}
};
localVue.prototype.$bvModal = {msgBoxConfirm: jest.fn()};

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
    const filters = [tv.DOCUMENT_PROPS.note, tv.DOCUMENT_PROPS.thumbnail_available];

    Object.values(tv.DOCUMENT_PROPS)
      .filter((prop) => {
        // Filter out note and thumbnail boolean of the test because we don't show those values
        return !filters.some((val) => {
          return val === prop;
        })
      })
      .forEach(function (documentData) {
        expect(wrapper.html()).toContain(documentData)
      })
  });
});

describe('FTLDocument script', () => {
  let wrapper;

  beforeEach(() => {
    // given
    axios.delete.mockResolvedValue(mockedDeleteResponse);
    wrapper = shallowMount(FTLDocument, {
      localVue,
      propsData: {doc: tv.DOCUMENT_PROPS}
    });
  });

  it('deleteDocument call api', async () => {
    wrapper.vm.$bvModal.msgBoxConfirm.mockResolvedValue(true);

    // when
    wrapper.vm.deleteDocument();
    await flushPromises();

    // then
    expect(axios.delete).toHaveBeenCalledWith(
      '/app/api/v1/documents/' + tv.DOCUMENT_PROPS.pid,
      axiosConfig
    );
  });

  it('deleteDocument emit event-delete-doc', async () => {
    wrapper.vm.$bvModal.msgBoxConfirm.mockResolvedValue(true);

    // when
    wrapper.vm.deleteDocument();
    await flushPromises();

    // then
    expect(wrapper.emitted('event-delete-doc')).toBeTruthy();
  });
});
