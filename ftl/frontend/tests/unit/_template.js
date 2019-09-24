import {createLocalVue, shallowMount} from '@vue/test-utils';

import axios from 'axios';
import BootstrapVue from "bootstrap-vue";
import flushPromises from "flush-promises"; // needed for async tests
import Vuex from 'vuex'; // TODO import Vuex if needed
import cloneDeep from "lodash.clonedeep"; // TODO import cloneDeep util if Vuex needed

import * as tv from './../tools/testValues.js'
import {axiosConfig} from "../../src/constants";

import Home from "../../src/views/Home"; // TODO import tested component here
// TODO Import all needed Vue components here

// Create clean Vue instance and set installed package to avoid warning
const localVue = createLocalVue();

// Mock BootstrapVue prototypes here (eg. localVue.prototype.$bvModal = {msgBoxConfirm: jest.fn()}; )
localVue.use(BootstrapVue); // avoid bootstrap vue warnings
localVue.use(Vuex); // TODO use Vuex store if needed
localVue.component('font-awesome-icon', jest.fn()); // avoid font awesome warnings

// Mock prototype and mixin bellow
localVue.prototype.$_ = (text, args='') => {return text + args};// i18n mock
localVue.prototype.$moment = () => {return {fromNow: jest.fn(), format: jest.fn()}}; // moment mock
localVue.prototype.$router = {push: jest.fn()}; // router mock
const mockedRouteName = jest.fn();
localVue.prototype.$route = {get name() { return mockedRouteName()}}; // router mock
const mockedMixinAlert = jest.fn();
localVue.mixin({methods: {mixinAlert: mockedMixinAlert}}); // mixinAlert mock

// TODO mock thumbnail generation if needed (when test add documents)
import {createThumbFromUrl} from '../../src/thumbnailGenerator';
import storeConfig from "@/store/storeConfig";
jest.mock('../../src/thumbnailGenerator', () => ({
  __esModule: true,
  createThumbFromUrl: jest.fn()
}));

// mock calls to api requests
jest.mock('axios', () => ({
  get: jest.fn(),
  // TODO add additional http word here if needed (post, patch...)
}));

// TODO store mocked response for tested api request here
const mockedGetResponseA = {
  data: tv.DOCUMENT_PROPS,
  status: 200,
  config: axiosConfig
};

// TODO mock tested component methods, computed, getters, mutations here
const mockedMethodA = jest.fn();
const mockedMethodB = jest.fn();
const mockedMethodC = jest.fn();
const mockedComputedA = jest.fn();
const mockedMutationA = jest.fn();
const mockedGetterWithParamA = jest.fn();
const mockedGetterWithoutParamA = jest.fn();

// TODO list method call in Component.mounted here
const mountedMocks = {
  methodB: mockedMethodB,
  methodC: mockedMethodC,
};

// TODO Generic tests structure example
describe('Component first type of test', () => {
  let wrapper;
  // defined const specific to this describe here
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(Home, {
      localVue,
      methods: Object.assign(
        {
          methodA: mockedMethodA,
          // Add other methods to mock here
        },
        mountedMocks
      ),
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('sync test', () => {
    // define const specific to this test here
    // define mocked library return value here
    // set required component component data here

    // when method is called / event is emitted...
    // then expect something
  });

  it('async test', async () => {
    // when method is called / event is emitted...
    await flushPromises(); // wait all pending promises are resolved/rejected
    // then expect something
  });

  it('unmock a method mocked in beforeEach to test it', () => {
    // restore original method to test it
    wrapper.setMethods({methodB: Home.methods.methodB});
    // when method is called / event is emitted...
    // then expect something
  });
});

// TODO add as many additional describe block and tests as needed to group tests by type, commons ones below
// TEMPLATE
describe('Component template', () => {
  it('renders properly text', () => {
    expect(wrapper.text()).toContain('text displayed in template');
  });
  // or
  it('renders properly html element', () => {
    const elementSelector= '#element-id';
    const elem = wrapper.find(elementSelector);
    expect(elem.is(elementSelector)).toBe(true);
  });
  // or
  it('renders properly component data', async () => {
    delete tv.DOCUMENT_PROPS.note;// remove unwanted data here
    Object.values(tv.DOCUMENT_PROPS).forEach(function(documentData){ expect(wrapper.html()).toContain(documentData) });
  });
});

// COMPUTED
describe('Component computed', () => {
  it('computedA return proper format', () => {});
});

// METHODS
describe('Component methods/watcher call proper methods', () => {
  it('methodA call proper methods', () => {});
});

describe('Component methods call api', () => {
  it('methodA call api', async () => {
    axios.get.mockResolvedValue(mockedGetResponseA);

    // when
    wrapper.vm.methodA();
    await flushPromises();

    // then
    expect(axios.get).toBeCalledWith('/app/api/v1/request/');
    expect(axios.get).toBeCalledTimes(1);
  });
});

describe('Component methods/watcher return proper value', () => {
  it('methodA return proper value', () => {});
});

describe('Component methods error handling', () => {
  it('methodA call mixinAlert in case of API error', async () => {
    // force an API error
    axios.get.mockRejectedValue('fakeError');

    // when
    wrapper.vm.methodA();
    await flushPromises();

    // then mixinAlert is called with proper message
    expect(mockedMixinAlert).toBeCalledTimes(1);
    expect(mockedMixinAlert.mock.calls[0][0]).toContain('Alert message');
  });
});

// EVENT
describe('Event emitted by component', () => {
  it('event-a emitted when calling methodA', async () => {
    const testedEvent = 'event-a';

    // when
    wrapper.vm.methodA();
    await flushPromises();

    // then
    expect(wrapper.emitted(testedEvent)).toBeTruthy();
    expect(wrapper.emitted(testedEvent).length).toBe(1);
    expect(wrapper.emitted(testedEvent)[0]).toEqual(['eventArg1']);
  });
});

describe('Event received and handled by component', () => {
  it('event-b call methodB', async () => {});
});

// VUEX
describe('Vuex tests', () => {
  let wrapper;
  let storeConfigCopy; // deep copy storeConfig for tests not to pollute it
  let store;

  beforeEach(() => {
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(
      Object.assign( // overwrite some mutations and getter to replace them with mocks
        storeConfigCopy,
        {
          mutations :
          {
            mutationA: mockedMutationA
          },
          getters :
          {
            getterWithParamA: () => mockedGetterWithParamA, // see https://vuex.vuejs.org/guide/getters.html#method-style-access
            getterWithoutParamA: mockedGetterWithoutParamA
          }
        }
      )
    );
    wrapper = shallowMount(Home, {
      localVue,
      store,
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('methodA commit change to store', async () => {
    // when
    mockedGetterWithParamA.mockReturnValue(true);
    wrapper.vm.methodA();

    // then
    expect(mockedMutationA).toBeCalledTimes(1);
    expect(mockedMutationA).toBeCalledWith(storeConfigCopy.state, 'mutationParam1');
  });
});
