import {createLocalVue, shallowMount} from '@vue/test-utils';

import axios from 'axios';
import BootstrapVue from "bootstrap-vue";
import flushPromises from "flush-promises"; // needed for async tests
import * as tv from './../tools/testValues.js'
import {axiosConfig} from "../../src/constants";

import FTLMoveDocument from "../../src/components/FTLMoveDocument";

const localVue = createLocalVue();

localVue.use(BootstrapVue); // avoid bootstrap vue warnings
localVue.component('font-awesome-icon', jest.fn()); // avoid font awesome warnings

localVue.prototype.$_ = (text, args) => {
  return text + ' ' + args
}; // i18n mock
localVue.prototype.$moment = () => {
  return {fromNow: jest.fn()}
}; // moment mock
localVue.prototype.$router = {push: jest.fn()}; // router mock
const mockedMixinAlert = jest.fn();
localVue.mixin({methods: {mixinAlert: mockedMixinAlert}}); // mixinAlert mock

// mock calls to api requests
jest.mock('axios', () => ({
  patch: jest.fn(),
}));

const mockedMoveFolderResponse = {
  data: tv.FOLDER_PROPS_WITH_PARENT,
  status: 200,
};

const mockedMoveDocumentResponse = {
  data: tv.DOCUMENT_PROPS_WITH_FOLDER,
  status: 200,
};

const mockedSelectedMoveTargetFolder = jest.fn();
const mockedIsRoot = jest.fn();

const documentProp = tv.DOCUMENT_PROPS;

describe('Component template', () => {
  let wrapper;
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(FTLMoveDocument, {
      localVue,
      propsData: {
        doc: documentProp
      },
      computed: {
        selectedMoveTargetFolder: mockedSelectedMoveTargetFolder,
        isRoot: mockedIsRoot
      }
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('renders properly template text', async () => {
    expect(wrapper.text()).toContain('No folder selected');
  });
});

describe('FTLMoveDocument computed', () => {
  let wrapper;

  it('getFolder return -1 when doc prop has no parent', () => {
    wrapper = shallowMount(FTLMoveDocument, {
      localVue,
      propsData: {
        doc: documentProp
      },
      computed: {
        selectedMoveTargetFolder: mockedSelectedMoveTargetFolder
      }
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted

    // when document props folder is null
    let testedValue = wrapper.vm.getFolder;

    // then
    expect(testedValue).toBe(-1);
  });

  it('selectedMoveTargetFolder return value from $store', () => {
    // TODO test call to vuex store here
  });

  it('isRoot return true when doc props get no parent', () => {
    wrapper = shallowMount(FTLMoveDocument, {
      localVue,
      propsData: {
        doc: documentProp
      },
      computed: {
        selectedMoveTargetFolder: mockedSelectedMoveTargetFolder
      }
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted

    // when document props folder is null
    let testedValue = wrapper.vm.isRoot;

    // then
    expect(testedValue).toBe(true);
  });

  it('isRoot return false when doc props get parent', () => {
    wrapper = shallowMount(FTLMoveDocument, {
      localVue,
      propsData: {
        doc: tv.DOCUMENT_PROPS_WITH_FOLDER
      },
      computed: {
        selectedMoveTargetFolder: mockedSelectedMoveTargetFolder
      }
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted

    // when document props folder is null
    let testedValue = wrapper.vm.isRoot;

    // then
    expect(testedValue).toBe(false);
  });
});

describe('Component methods call api', () => {
  let wrapper;
  beforeEach(() => {
    axios.patch.mockResolvedValue(mockedMoveDocumentResponse);
    mockedSelectedMoveTargetFolder.mockReturnValue(tv.FOLDER_PROPS_VARIANT);

    wrapper = shallowMount(FTLMoveDocument, {
      localVue,
      propsData: {doc: documentProp},
      computed: {
        selectedMoveTargetFolder: mockedSelectedMoveTargetFolder,
        isRoot: mockedIsRoot
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
      axiosConfig
    );
    expect(axios.patch).toHaveBeenCalledTimes(1);
  });
});

describe('Component methods error handling', () => {
  let wrapper;
  beforeEach(() => {
    axios.patch.mockRejectedValue('fakeError');
    mockedSelectedMoveTargetFolder.mockReturnValue(tv.FOLDER_PROPS_VARIANT);

    wrapper = shallowMount(FTLMoveDocument, {
      localVue,
      propsData: {doc: documentProp},
      computed: {
        selectedMoveTargetFolder: mockedSelectedMoveTargetFolder,
        isRoot: mockedIsRoot
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
    expect(mockedMixinAlert.mock.calls[0][0]).toContain('Could not move document');
  });
});

describe('Event emitted by component', () => {
  let wrapper;
  beforeEach(() => {
    axios.patch.mockResolvedValue(mockedMoveDocumentResponse);
    mockedSelectedMoveTargetFolder.mockReturnValue(tv.FOLDER_PROPS_VARIANT);

    wrapper = shallowMount(FTLMoveDocument, {
      localVue,
      propsData: {doc: documentProp},
      computed: {
        selectedMoveTargetFolder: mockedSelectedMoveTargetFolder,
        isRoot: mockedIsRoot
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
    expect(wrapper.emitted(testedEvent)[0]).toEqual([mockedSelectedMoveTargetFolder()]);
  });
});
