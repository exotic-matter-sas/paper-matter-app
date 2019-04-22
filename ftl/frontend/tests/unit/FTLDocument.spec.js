import { shallowMount } from '@vue/test-utils';

import axios from 'axios';

import FTLDocument from '@/components/FTLDocument.vue';
import * as tv from './../tools/testValues.js'

jest.mock('axios', () => ({
  delete: jest.fn()
}));

describe('FTLDocument template', () => {
  it('renders properly document data', () => {
    const wrapper = shallowMount(FTLDocument, {
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
    wrapper = shallowMount(FTLDocument, {
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