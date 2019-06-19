import {createLocalVue, shallowMount} from '@vue/test-utils';

import BootstrapVue from "bootstrap-vue";

import * as tv from './../tools/testValues.js'
import FTLNavbar from "../../src/components/FTLNavbar";

const localVue = createLocalVue();
localVue.use(BootstrapVue); // to avoid warning on tests execution
localVue.prototype.$_ = (text) => {
  return text;
}; // i18n mock
localVue.prototype.$moment = jest.fn();

describe('FTLNavbar template', () => {
  const wrapper = shallowMount(FTLNavbar, {
    localVue: localVue,
    propsData: tv.ACCOUNT_PROPS
  });

  it('renders properly account name', () => {
    expect(wrapper.text()).toMatch('Jon Snow')
  })
});
