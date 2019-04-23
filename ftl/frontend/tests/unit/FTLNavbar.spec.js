import { mount, createLocalVue } from '@vue/test-utils';

import BootstrapVue from "bootstrap-vue";

import * as tv from './../tools/testValues.js'
import FTLNavbar from "../../src/components/FTLNavbar";

const localVue = createLocalVue();
localVue.use(BootstrapVue); // to avoid warning on tests execution


describe('FTLNavbar template', () => {
  it('renders properly account name', () => {
    const wrapper = mount(FTLNavbar, {
      localVue: localVue,
      propsData: tv.ACCOUNT_PROPS
    });
    expect(wrapper.text()).toMatch('John Doe')
  })
});