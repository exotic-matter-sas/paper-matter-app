import { createLocalVue, mount } from '@vue/test-utils';

import axios from 'axios';
import BootstrapVue from "bootstrap-vue";

import * as tv from './../tools/testValues.js'
import FTLDocument from "../../src/components/FTLDocument";

const localVue = createLocalVue();
localVue.use(BootstrapVue); // to avoid warning on tests execution

jest.mock('axios', () => ({
  delete: jest.fn()
}));


describe('FTLDocument template', () => {
  it('renders properly document data', () => {
    const wrapper = mount(FTLDocument, {
      localVue,
      propsData: { doc: tv.DOCUMENT_PROPS }
    });
    Object.values(tv.DOCUMENT_PROPS).forEach(function(documentData){
      expect(wrapper.html()).toContain(documentData)
    })
  });
});

describe('FTLDocument script', () => {
  const mockedDeleteResponse  = {
    data: {},
    status: 204,
    config: tv.AXIOS_CONF
  };
  let wrapper;
  let delete_button;

  beforeEach(() => {
    // given
    axios.delete.mockReturnValue(Promise.resolve(mockedDeleteResponse));
    wrapper = mount(FTLDocument, {
      localVue,
      propsData: { doc: tv.DOCUMENT_PROPS }
    });
    delete_button = wrapper.find('.deleteDocument');
  });

  it('deleteDocument call api', () => {
    // when
    delete_button.trigger('click');

    // then
    expect(axios.delete).toHaveBeenCalledWith(
        '/app/api/v1/documents/' + tv.DOCUMENT_PROPS.pid,
        tv.AXIOS_CONF
    );
  });
  it('deleteDocument emit event-delete-doc', done => {
    // when
    delete_button.trigger('click');

    // then
    wrapper.vm.$nextTick(() => {
      expect(wrapper.emitted('event-delete-doc')).toBeTruthy();
      done();
    });
  });
});