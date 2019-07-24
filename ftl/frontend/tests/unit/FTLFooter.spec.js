import { shallowMount, createLocalVue } from '@vue/test-utils';

import BootstrapVue from "bootstrap-vue";

import FTLFooter from "@/components/FTLFooter";

const localVue = createLocalVue();
localVue.use(BootstrapVue); // to avoid warning on tests execution
localVue.prototype.$_ = (text) => { return text; }; // i18n mock


describe('FTLFooter template', () => {
  const wrapper = shallowMount(FTLFooter, {
    localVue: localVue
  });

  it('renders properly account name', () => {
    expect(wrapper.text()).toContain('Made with ❤ by', 'Exotic Matter')
  })
});
