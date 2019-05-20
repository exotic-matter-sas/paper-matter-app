import { createLocalVue, shallowMount } from '@vue/test-utils';

import axios from 'axios';
import BootstrapVue from "bootstrap-vue";

import * as tv from './../tools/testValues.js'
import FTLDocument from "../../src/components/FTLDocument";

const localVue = createLocalVue();
localVue.use(BootstrapVue); // to avoid warning on tests execution
localVue.prototype.$_ = (text) => { return text; }; // i18n mock

jest.mock('axios', () => ({
  delete: jest.fn()
}));

const mockedDeleteResponse  = {
  data: {},
  status: 204,
  config: tv.AXIOS_CRSF_CONF
};


describe('FTLDocument template', () => {
  const wrapper = shallowMount(FTLDocument, {
    localVue,
    propsData: { doc: tv.DOCUMENT_PROPS }
  });

  it('renders properly document data', () => {
    Object.values(tv.DOCUMENT_PROPS).forEach(function(documentData){
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
      propsData: { doc: tv.DOCUMENT_PROPS }
    });
  });

  it('deleteDocument call api', () => {
    // when
    wrapper.vm.deleteDocument();

    // then
    expect(axios.delete).toHaveBeenCalledWith(
        '/app/api/v1/documents/' + tv.DOCUMENT_PROPS.pid,
        tv.AXIOS_CRSF_CONF
    );
  });
  it('deleteDocument emit event-delete-doc', done => {
    // when
    wrapper.vm.deleteDocument();

    // then
    wrapper.vm.$nextTick(() => {
      expect(wrapper.emitted('event-delete-doc')).toBeTruthy();
      done();
    });
  });
});
