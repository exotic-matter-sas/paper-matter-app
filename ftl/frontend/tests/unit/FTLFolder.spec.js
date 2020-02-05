/*
 * Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
 * Licensed under the BSL License. See LICENSE in the project root for license information.
 */

import {createLocalVue, shallowMount} from '@vue/test-utils';

import BootstrapVue from "bootstrap-vue";

import * as tv from './../tools/testValues.js';
import FTLFolder from "../../src/components/FTLFolder";

const localVue = createLocalVue();
localVue.use(BootstrapVue); // to avoid warning on tests execution
localVue.prototype.$t = (text) => {
  return text;
}; // i18n mock
localVue.prototype.$tc = (text, args='') => {return text + args};// i18n mock
localVue.prototype.$moment = () => {
  return {fromNow: jest.fn()}
};

describe('FTLFolder template', () => {
  const wrapper = shallowMount(FTLFolder, {
    localVue,
    propsData: {folder: tv.FOLDER_PROPS}
  });

  it('renders properly folder data', () => {
    expect(wrapper.html()).toContain(tv.FOLDER_PROPS.name)
  });
});
