import {createLocalVue, shallowMount} from '@vue/test-utils';

import axios from 'axios';
import BootstrapVue from "bootstrap-vue";
import flushPromises from "flush-promises"; // needed for async tests

import * as tv from './../tools/testValues.js'
import {axiosConfig} from "../../src/constants";

import FTLSelectableFolder from "../../src/components/FTLSelectableFolder";
import Vuex from "vuex";
import storeConfig from "@/store/storeConfig";
import cloneDeep from "lodash.clonedeep";

// Create clean Vue instance and set installed package to avoid warning
const localVue = createLocalVue();

// Mock BootstrapVue prototypes here (eg. localVue.prototype.$bvModal = {msgBoxConfirm: jest.fn()}; )
localVue.use(BootstrapVue); // avoid bootstrap vue warnings
localVue.use(Vuex);
localVue.component('font-awesome-icon', jest.fn()); // avoid font awesome warnings

// Mock prototype and mixin bellow
localVue.prototype.$_ = (text, args='') => {return text + args};// i18n mock
localVue.prototype.$moment = () => {return {fromNow: jest.fn()}}; // moment mock
localVue.prototype.$router = {push: jest.fn()}; // router mock
localVue.prototype.$store = {commit: jest.fn()}; // vuex mock
const mockedMixinAlert = jest.fn();
localVue.mixin({methods: {mixinAlert: mockedMixinAlert}}); // mixinAlert mock

const mockedSelectPanelFolder = jest.fn();

const folder = tv.FOLDER_PROPS;

describe('FTLSelectableFolder template', () => {
  let wrapper;
  let storeConfigCopy;
  let store;
  // defined const specific to this describe here
  beforeEach(() => {
    store = new Vuex.Store(storeConfigCopy);
    wrapper = shallowMount(FTLSelectableFolder, {
      localVue,
      store,
      propsData: {folder},
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('renders properly component template', () => {
    expect(wrapper.text()).toContain(folder.name);
  });
});

describe('watcher set data', () => {
  let wrapper;
  let storeConfigCopy;
  let store;
  // defined const specific to this describe here
  beforeEach(() => {
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(
      Object.assign(
        storeConfigCopy,
        {
          mutations :
          {
            selectPanelFolder: mockedSelectPanelFolder,
          }
        }
      )
    );
    wrapper = shallowMount(FTLSelectableFolder, {
      localVue,
      store,
      propsData: {folder},
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('panelSelectedFolder watcher set state to false if selected folder change', () => {
    wrapper.setData({state: true});

    // when
    storeConfigCopy.state.panelSelectedFolder = tv.FOLDER_PROPS_VARIANT;

    // then
    expect(wrapper.vm.state).toBe(false);
  });

  it('state watcher store data to Vuex', () => {
    // when
    wrapper.setData({state: true});

    // then
    expect(mockedSelectPanelFolder).toBeCalledTimes(1);
    expect(mockedSelectPanelFolder).toBeCalledWith(storeConfigCopy.state, folder);

    // when
    wrapper.setData({state: false});

    // then
    expect(mockedSelectPanelFolder).toBeCalledTimes(2);
    expect(mockedSelectPanelFolder).toBeCalledWith(storeConfigCopy.state, null);
  });
});

describe('method or watcher emit event', () => {
  let wrapper;
  let storeConfigCopy;
  let store;
  beforeEach(() => {
    storeConfigCopy = cloneDeep(storeConfig);
    store = new Vuex.Store(storeConfigCopy);
    wrapper = shallowMount(FTLSelectableFolder, {
      localVue,
      store,
      propsData: {folder},
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('event-navigate-folder emitted when calling navigateToFolder', async () => {
    const testedEvent = 'event-navigate-folder';

    // when
    wrapper.vm.navigateToFolder();
    await flushPromises();

    // then
    expect(wrapper.emitted(testedEvent)).toBeTruthy();
    expect(wrapper.emitted(testedEvent).length).toBe(1);
    expect(wrapper.emitted(testedEvent)[0]).toEqual([folder]);
  });

  it('event-select-folder emitted when setting state', async () => {
    const testedEvent = 'event-select-folder';

    // when
    wrapper.setData({state: true});
    await flushPromises();

    // then
    expect(wrapper.emitted(testedEvent)).toBeTruthy();
    expect(wrapper.emitted(testedEvent).length).toBe(1);
    expect(wrapper.emitted(testedEvent)[0]).toEqual([folder]);
  });

  it('event-unselect-folder emitted when unsetting state', async () => {
    const testedEvent = 'event-unselect-folder';
    wrapper.setData({state: true});

    // when
    wrapper.setData({state: false});
    await flushPromises();

    // then
    expect(wrapper.emitted(testedEvent)).toBeTruthy();
    expect(wrapper.emitted(testedEvent).length).toBe(1);
  });
});
