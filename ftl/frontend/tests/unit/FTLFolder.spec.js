import {createLocalVue, shallowMount} from '@vue/test-utils';

import BootstrapVue from "bootstrap-vue";

import * as tv from './../tools/testValues.js';
import FTLFolder from "../../src/components/FTLFolder";

const localVue = createLocalVue();
localVue.use(BootstrapVue); // to avoid warning on tests execution
localVue.prototype.$_ = (text) => {
  return text;
}; // i18n mock
localVue.prototype.$moment = jest.fn();

describe('FTLFolder template', () => {
  const wrapper = shallowMount(FTLFolder, {
    localVue,
    propsData: {folder: tv.FOLDER_PROPS}
  });

  it('renders properly folder data', () => {
    expect(wrapper.html()).toContain(tv.FOLDER_PROPS.name)
  });
});
