import { shallowMount, createLocalVue } from '@vue/test-utils';

import BootstrapVue from "bootstrap-vue";

import * as tv from './../tools/testValues.js'
import FTLHeader from "@/components/FTLHeader";

const localVue = createLocalVue();
localVue.use(BootstrapVue); // to avoid warning on tests execution
localVue.prototype.$_ = (text) => { return text; }; // i18n mock


describe('FTLHeader template', () => {
  const wrapper = shallowMount(FTLHeader, {
    localVue: localVue,
    propsData: tv.ACCOUNT_PROPS
  });

  it('renders properly account name', () => {
    expect(wrapper.text()).toMatch('Jon Snow')
  })
});
