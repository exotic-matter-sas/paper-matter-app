/*
 * Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
 * Licensed under the BSL License. See LICENSE in the project root for license information.
 */

import {createLocalVue, shallowMount} from '@vue/test-utils';

import BootstrapVue from "bootstrap-vue";

import * as tv from './../tools/testValues.js'
import FTLHeader from "@/components/FTLHeader";

// Create clean Vue instance and set installed package to avoid warning
const localVue = createLocalVue();

localVue.use(BootstrapVue); // avoid bootstrap vue warnings
localVue.component('font-awesome-icon', jest.fn()); // avoid font awesome warnings

localVue.prototype.$t = (text) => {
  return text
}; // i18n mock
localVue.prototype.$tc = (text, args='') => {return text + args};// i18n mock
localVue.prototype.$moment = () => {
  return {fromNow: jest.fn()}
}; // moment mock
localVue.prototype.$router = {push: jest.fn()}; // router mock
localVue.prototype.$route = {query: jest.fn()}; // router mock

const mockedDoSearch = jest.fn();
const mockedUpdate = jest.fn();

const mountedMocks = {
  update: mockedUpdate,
};

describe('FTLHeader template', () => {
  let wrapper;

  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(FTLHeader, {
      localVue,
      propsData: tv.ACCOUNT_PROPS,
      stubs: ['router-link'],
      methods: mountedMocks,
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('renders properly account name', () => {
    expect(wrapper.text()).toMatch('Jon Snow')
  })
});

describe('FTLHeader methods call proper methods', () => {
  let wrapper;
  const testedSearch = 'bingo!';

  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(FTLHeader, {
      localVue,
      propsData: tv.ACCOUNT_PROPS,
      methods: Object.assign(
        {
          doSearch: mockedDoSearch,
        },
        mountedMocks
      ),
      stubs: ['router-link'],
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('clear reset search data and push home to router', () => {
    //when
    wrapper.setData({search: testedSearch});
    wrapper.vm.clear();

    //then
    expect(wrapper.vm.search).toEqual('');
    expect(wrapper.vm.$router.push).toHaveBeenCalledTimes(1);
    expect(wrapper.vm.$router.push).toHaveBeenCalledWith({name: 'home'});
  });

  it('doSearch push search to router', () => {
    // restore original method to test it
    wrapper.setMethods({doSearch: FTLHeader.methods.doSearch});

    //when
    wrapper.setData({search: testedSearch});
    wrapper.vm.doSearch();

    //then
    expect(wrapper.vm.$router.push).toHaveBeenCalledTimes(1);
    expect(wrapper.vm.$router.push).toHaveBeenCalledWith({name: 'home-search', params: {search: testedSearch}});
  });
});
