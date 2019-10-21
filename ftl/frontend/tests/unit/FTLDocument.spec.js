import {createLocalVue, shallowMount} from '@vue/test-utils';

import axios from 'axios';
import BootstrapVue from "bootstrap-vue";
import flushPromises from "flush-promises"; // needed for async tests
import * as tv from './../tools/testValues.js'
import {axiosConfig} from "../../src/constants";

import FTLDocument from "../../src/components/FTLDocument";
import Vuex from "vuex";
import storeConfig from "@/store/storeConfig";
import cloneDeep from "lodash.clonedeep";

const localVue = createLocalVue();
// mock BootstrapVue Modal method, need to be before use BootstrapVue line
localVue.prototype.$bvModal = {msgBoxConfirm: jest.fn()};
localVue.use(BootstrapVue); // avoid bootstrap vue warnings
localVue.use(Vuex);

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

const mockedUnselectDocument = jest.fn();
const mockedSelectDocuments = jest.fn();

const mockedDeleteResponse = {
  data: {},
  status: 204,
  config: axiosConfig
};

describe('FTLDocument template', () => {
  let storeConfigCopy = cloneDeep(storeConfig);
  let store = new Vuex.Store(storeConfigCopy);

  const wrapper = shallowMount(FTLDocument, {
    localVue,
    store,
    propsData: {doc: tv.DOCUMENT_PROPS},
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
  let storeConfigCopy;
  let store;
  const testedDocument = tv.DOCUMENT_PROPS;

  beforeEach(() => {
    // given
    axios.delete.mockResolvedValue(mockedDeleteResponse);
    localVue.prototype.$bvModal.msgBoxConfirm.mockResolvedValue(true);
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(
      Object.assign(
        storeConfigCopy,
        {
          mutations:
            {
              unselectDocument: mockedUnselectDocument,
              selectDocuments: mockedSelectDocuments,
            }
        }
      )
    );
    wrapper = shallowMount(FTLDocument, {
      localVue,
      store,
      propsData: {doc: testedDocument},
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

  it('toggleSelection commit changes to store', () => {
    // when
    wrapper.vm.toggleSelection();

    // then
    expect(mockedSelectDocuments).toBeCalledTimes(1);
    expect(mockedSelectDocuments).toBeCalledWith(storeConfigCopy.state, [testedDocument]);

    // when
    storeConfigCopy.state.selectedDocumentsHome.push(testedDocument);
    wrapper.vm.toggleSelection();

    // then
    expect(mockedUnselectDocument).toBeCalledTimes(1);
    expect(mockedUnselectDocument).toBeCalledWith(storeConfigCopy.state, testedDocument);
  });
});
