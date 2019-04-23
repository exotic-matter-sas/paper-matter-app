import { createLocalVue, mount } from '@vue/test-utils';

import BootstrapVue from "bootstrap-vue";

import * as tv from './../tools/testValues.js'
import FTLFolder from "../../src/components/FTLFolder";

const localVue = createLocalVue();
localVue.use(BootstrapVue); // to avoid warning on tests execution


describe('FTLFolder template', () => {
  it('renders properly folder data', () => {
    const wrapper = mount(FTLFolder, {
      localVue,
      propsData: { folder: tv.FOLDER_PROPS }
    });
    expect(wrapper.html()).toContain(tv.FOLDER_PROPS.name)
  });
});