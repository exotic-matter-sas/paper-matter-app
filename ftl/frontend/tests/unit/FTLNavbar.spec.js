import {createLocalVue, shallowMount} from '@vue/test-utils';

import BootstrapVue from "bootstrap-vue";

import * as tv from './../tools/testValues.js'

import FTLNavbar from "../../src/components/FTLNavbar";

// Create clean Vue instance and set installed package to avoid warning
const localVue = createLocalVue();

localVue.use(BootstrapVue); // avoid bootstrap vue warnings
localVue.component('font-awesome-icon', jest.fn()); // avoid font awesome warnings

localVue.prototype.$_ = (text) => {return text}; // i18n mock
localVue.prototype.$moment = () => {return {fromNow: jest.fn()}}; // moment mock
localVue.prototype.$router = {push: jest.fn()}; // router mock

const mockedDoSearch = jest.fn();

describe('FTLNavbar template', () => {
  let wrapper;

  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(FTLNavbar, {
      localVue,
      propsData: tv.ACCOUNT_PROPS,
      stubs: ['router-link']
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('renders properly account name', () => {
    expect(wrapper.text()).toMatch('Jon Snow')
  })
});

describe('FTLNavbar methods call proper methods', () => {
  let wrapper;
  const testedSearch = 'bingo!';

  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(FTLNavbar, {
      localVue,
      propsData: tv.ACCOUNT_PROPS,
      methods: { doSearch: mockedDoSearch},
      stubs: ['router-link'],
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('clear call doSearch', () => {
    //when
    wrapper.setData({search: testedSearch});
    wrapper.vm.clear();

    //then
    expect(wrapper.vm.search).toEqual('');
    expect(mockedDoSearch).toHaveBeenCalledTimes(1);
  });

  it('doSearch push search to router', () => {
    // restore original method to test it
    wrapper.setMethods({doSearch: FTLNavbar.methods.doSearch});

    //when
    wrapper.setData({search: testedSearch});
    wrapper.vm.doSearch();

    //then
    expect(wrapper.vm.$router.push).toHaveBeenCalledTimes(1);
    expect(wrapper.vm.$router.push).toHaveBeenCalledWith({name: 'home', query: {q: testedSearch}});
  });
});
