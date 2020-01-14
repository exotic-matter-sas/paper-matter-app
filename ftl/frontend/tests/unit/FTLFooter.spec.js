/*
 * Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
 * Licensed under the BSL License. See LICENSE in the project root for license information.
 */

import {createLocalVue, shallowMount} from '@vue/test-utils';
import VueI18n from 'vue-i18n'

import BootstrapVue from "bootstrap-vue";

import FTLFooter from "@/components/FTLFooter";

const localVue = createLocalVue();
localVue.use(BootstrapVue); // to avoid warning on tests execution
localVue.use(VueI18n);
localVue.prototype.$t = (text) => {
  return text;
}; // i18n mock


describe('FTLFooter template', () => {
  const wrapper = shallowMount(FTLFooter, {
    localVue: localVue
  });

  it('renders properly account name', () => {
    expect(wrapper.text()).toContain('Made with ❤ by', 'Exotic Matter')
  })
});
