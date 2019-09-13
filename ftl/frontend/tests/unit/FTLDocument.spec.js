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

localVue.prototype.$_ = (text) => {
  return text
}; // i18n mock
localVue.prototype.$moment = () => {
  return {fromNow: jest.fn(), format: jest.fn()}
}; // moment mock
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
    propsData: {doc: tv.DOCUMENT_PROPS},
    computed: {
      storeSelected: false
    }
  });

  it('renders properly document data', () => {
    let document_props_to_test = tv.DOCUMENT_PROPS;
    delete document_props_to_test.note;
    delete document_props_to_test.created;
    delete document_props_to_test.ftl_folder;
    Object.values(document_props_to_test).forEach(function (documentData) {
      expect(wrapper.html()).toContain(documentData)
    })
  });
});

describe('FTLDocument methods', () => {
  let wrapper;
  const testedDocument = tv.DOCUMENT_PROPS;
  const defaultStoreSelectedValue = false;

  beforeEach(() => {
    // given
    axios.delete.mockResolvedValue(mockedDeleteResponse);
    localVue.prototype.$bvModal.msgBoxConfirm.mockResolvedValue(true);
    wrapper = shallowMount(FTLDocument, {
      localVue,
      propsData: {doc: testedDocument},
      computed: {
        storeSelected: defaultStoreSelectedValue
      }
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

  it('clickDoc toggle storeSelected in store', () => {
    // TODO vuex test
  });
});

describe('FTLDocument computed', () => {
    // TODO vuex test
});
