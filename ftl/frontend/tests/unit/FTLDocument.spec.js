import { createLocalVue, shallowMount } from '@vue/test-utils';

import axios from 'axios';
import BootstrapVue from "bootstrap-vue";

import * as tv from './../tools/testValues.js'
import FTLDocument from "../../src/components/FTLDocument";
import {axiosConfig} from "../../src/constants";

const localVue = createLocalVue();
localVue.use(BootstrapVue); // to avoid warning on tests execution
localVue.prototype.$_ = (text) => { return text; }; // i18n mock

jest.mock('axios', () => ({
  delete: jest.fn()
}));

const mockedDeleteResponse  = {
  data: {},
  status: 204,
  config: axiosConfig
};


describe('FTLDocument template', () => {
  const wrapper = shallowMount(FTLDocument, {
    localVue,
    propsData: { doc: tv.DOCUMENT_PROPS }
  });

  it('renders properly document data', () => {
    let document_props_to_test = tv.DOCUMENT_PROPS;
    delete document_props_to_test.note;
    Object.values(document_props_to_test).forEach(function(documentData){
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
        axiosConfig
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
