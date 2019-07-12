import {createLocalVue, shallowMount} from '@vue/test-utils';

import axios from 'axios';
import BootstrapVue from "bootstrap-vue";
import flushPromises from "flush-promises"; // needed for async tests

import * as tv from './../tools/testValues.js'
import {axiosConfig} from "../../src/constants";

import FTLSelectableFolder from "../../src/components/FTLSelectableFolder";

// Create clean Vue instance and set installed package to avoid warning
const localVue = createLocalVue();

// Mock BootstrapVue prototypes here (eg. localVue.prototype.$bvModal = {msgBoxConfirm: jest.fn()}; )
localVue.use(BootstrapVue); // avoid bootstrap vue warnings
localVue.component('font-awesome-icon', jest.fn()); // avoid font awesome warnings

// Mock prototype and mixin bellow
localVue.prototype.$_ = (text, args='') => {return text + args};// i18n mock
localVue.prototype.$moment = () => {return {fromNow: jest.fn()}}; // moment mock
localVue.prototype.$router = {push: jest.fn()}; // router mock
localVue.prototype.$store = {commit: jest.fn()}; // vuex mock
const mockedMixinAlert = jest.fn();
localVue.mixin({methods: {mixinAlert: mockedMixinAlert}}); // mixinAlert mock

const mockedDbClickFolder = jest.fn();
const mockedClickFolder = jest.fn();
const mockedGlobalSelected = jest.fn();

const folder = tv.FOLDER_PROPS;

describe('FTLSelectableFolder template', () => {
  let wrapper;
  // defined const specific to this describe here
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(FTLSelectableFolder, {
      localVue,
      propsData: { folder },
      computed: {
        globalSelected: mockedGlobalSelected
      }
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('renders properly component template', () => {
    expect(wrapper.text()).toContain(folder.name);
  });
});

// TODO Vuex test here
describe('FTLSelectableFolder computed and methode store data to Vuex', () => {
  it('globalSelected store data to vuex', () => {});
  it('clickFolder with no folder selected store data to vuex', () => {});
  it('clickFolder with folder selected store data to vuex', () => {});
});

describe('FTLSelectableFolder watcher set data', () => {
  it('globalSelected watcher set data if selected folder change', () => {});
});

describe('Event emitted by component', () => {
  let wrapper;
  // defined const specific to this describe here
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(FTLSelectableFolder, {
      localVue,
      propsData: { folder },
      computed: {
        globalSelected: mockedGlobalSelected
      }
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('event-navigate-folder emitted when calling dbClickFolder', async () => {
    const testedEvent = 'event-navigate-folder';

    // when
    wrapper.vm.dbClickFolder();
    await flushPromises();

    // then
    expect(wrapper.emitted(testedEvent)).toBeTruthy();
    expect(wrapper.emitted(testedEvent).length).toBe(1);
    expect(wrapper.emitted(testedEvent)[0]).toEqual([folder]);
  });

  it('event-select-folder emitted when calling clickFolder and no folder selected', async () => {
    const testedEvent = 'event-select-folder';

    // when
    wrapper.vm.clickFolder();
    await flushPromises();

    // then
    expect(wrapper.emitted(testedEvent)).toBeTruthy();
    expect(wrapper.emitted(testedEvent).length).toBe(1);
    expect(wrapper.emitted(testedEvent)[0]).toEqual([folder]);
  });

  it('event-unselect-folder emitted when calling clickFolder and no folder selected', async () => {
    const testedEvent = 'event-unselect-folder';
    wrapper.setData({selected: true});

    // when
    wrapper.vm.clickFolder();
    await flushPromises();

    // then
    expect(wrapper.emitted(testedEvent)).toBeTruthy();
    expect(wrapper.emitted(testedEvent).length).toBe(1);
  });
});
