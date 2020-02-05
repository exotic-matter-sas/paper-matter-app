/*
 * Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
 * Licensed under the BSL License. See LICENSE in the project root for license information.
 */

import {createLocalVue, shallowMount} from '@vue/test-utils';

import axios from 'axios';
import BootstrapVue from "bootstrap-vue";
import flushPromises from "flush-promises"; // needed for async tests
import * as tv from './../tools/testValues.js'
import {axiosConfig} from "../../src/constants";

import FTLMoveDocuments from "../../src/components/FTLMoveDocuments";

const localVue = createLocalVue();

localVue.use(BootstrapVue); // avoid bootstrap vue warnings
localVue.component('font-awesome-icon', jest.fn()); // avoid font awesome warnings

localVue.prototype.$t = (text, args) => {
  return text + ' ' + args
}; // i18n mock
localVue.prototype.$tc = (text, args='') => {return text + args};// i18n mock
localVue.prototype.$moment = () => {
  return {fromNow: jest.fn()}
}; // moment mock
localVue.prototype.$router = {push: jest.fn()}; // router mock
localVue.prototype.$store = {commit: jest.fn()}; // vuex mock
const mockedMixinAlert = jest.fn();
localVue.mixin({methods: {mixinAlert: mockedMixinAlert, mixinAlertWarning: mockedMixinAlert}}); // mixin alert

// mock calls to api requests
jest.mock('axios', () => ({
  patch: jest.fn(),
}));

const mockedMoveDocumentResponse = {
  data: tv.DOCUMENT_PROPS_WITH_FOLDER_MOVED,
  status: 200,
};

const mockedSelectedMoveTargetFolder = jest.fn();
const mockedSelectedMoveTargetFolderResponse = {id: tv.FOLDER_PROPS.id, name: tv.FOLDER_PROPS.name};

const documentProp = tv.DOCUMENT_PROPS;

describe('Component template', () => {
  let wrapper;
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(FTLMoveDocuments, {
      localVue,
      propsData: {
        docs: [documentProp]
      },
      computed: {
        selectedMoveTargetFolder: mockedSelectedMoveTargetFolder,
      }
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('renders properly template text', async () => {
    expect(wrapper.text()).toContain('No folder selected');
  });

  it('renders properly html element', () => {
    const elementSelector = '#modal-move-documents';
    const elem = wrapper.find(elementSelector);
    expect(elem.is(elementSelector)).toBe(true);
  });

  it('renders properly template data for 1 document', () => {
    expect(wrapper.text()).toContain(documentProp.title);
  });

  it('renders properly template data for several documents', () => {
    // overwrite docs prop with only 1 doc
    const documentsList = [documentProp, tv.DOCUMENT_PROPS_VARIANT];
    wrapper.setData({ docs: documentsList});

    expect(wrapper.text()).toContain(documentsList.length);
  });
});

describe('FTLMoveDocuments computed', () => {
  let wrapper;

  it('selectedMoveTargetFolder return value from $store', () => {
    // TODO test call to vuex store here
  });
});

describe('Component methods call api', () => {
  let wrapper;
  beforeEach(() => {
    axios.patch.mockResolvedValue(mockedMoveDocumentResponse);
    mockedSelectedMoveTargetFolder.mockReturnValue(tv.FOLDER_PROPS_VARIANT);

    wrapper = shallowMount(FTLMoveDocuments, {
      localVue,
      propsData: {docs: [documentProp, tv.DOCUMENT_PROPS_WITH_FOLDER]},
      computed: {
        selectedMoveTargetFolder: mockedSelectedMoveTargetFolder,
      }
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('moveDocument call api', async () => {
    // when
    wrapper.vm.moveDocument();

    // then
    expect(axios.patch).toHaveBeenCalledWith(
      '/app/api/v1/documents/' + documentProp.pid,
      {ftl_folder: tv.FOLDER_PROPS_VARIANT.id},
      {...axiosConfig, docPid: documentProp.pid}
    );
    expect(axios.patch).toHaveBeenCalledWith(
      '/app/api/v1/documents/' + tv.DOCUMENT_PROPS_WITH_FOLDER.pid,
      {ftl_folder: tv.FOLDER_PROPS_VARIANT.id},
      {...axiosConfig, docPid: tv.DOCUMENT_PROPS_WITH_FOLDER.pid}
    );
    expect(axios.patch).toHaveBeenCalledTimes(2);
  });
});

describe('Component methods error handling', () => {
  let wrapper;
  beforeEach(() => {
    axios.patch.mockRejectedValue('fakeError');
    mockedSelectedMoveTargetFolder.mockReturnValue(tv.FOLDER_PROPS_VARIANT);

    wrapper = shallowMount(FTLMoveDocuments, {
      localVue,
      propsData: {docs: [documentProp]},
      computed: {
        selectedMoveTargetFolder: mockedSelectedMoveTargetFolder,
      }
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('moveFolder call mixinAlert in case of error', async () => {
    // force an error

    // when
    wrapper.vm.moveDocument();
    await flushPromises();

    // then mixinAlert is called with proper message
    expect(mockedMixinAlert).toHaveBeenCalledTimes(1);
    expect(mockedMixinAlert.mock.calls[0][0]).toContain('document moved successfully');
  });
});

describe('Event emitted by component', () => {
  let wrapper;
  beforeEach(() => {
    axios.patch.mockResolvedValue(mockedMoveDocumentResponse);
    mockedSelectedMoveTargetFolder.mockReturnValue(mockedSelectedMoveTargetFolderResponse);

    wrapper = shallowMount(FTLMoveDocuments, {
      localVue,
      propsData: {docs: [documentProp]},
      computed: {
        selectedMoveTargetFolder: mockedSelectedMoveTargetFolder,
      }
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('event-document-moved emitted when calling moveDocument', async () => {
    const testedEvent = 'event-document-moved';

    // when
    wrapper.vm.moveDocument();
    await flushPromises();

    // then
    expect(wrapper.emitted(testedEvent)).toBeTruthy();
    expect(wrapper.emitted(testedEvent).length).toBe(1);
    expect(wrapper.emitted(testedEvent)[0]).toEqual([{
      'doc': tv.DOCUMENT_PROPS_WITH_FOLDER_MOVED,
      'target_folder': mockedSelectedMoveTargetFolderResponse
    }]);
  });
});
