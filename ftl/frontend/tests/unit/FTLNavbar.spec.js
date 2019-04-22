import { shallowMount } from '@vue/test-utils'

import FTLNavbar from '@/components/FTLNavbar.vue'
import * as tv from './../tools/testValues.js'

describe('FTLNavbar template', () => {
  it('renders properly account name', () => {
    const wrapper = shallowMount(FTLNavbar, {
      propsData: tv.ACCOUNT_PROPS
    });
    expect(wrapper.text()).toMatch('John Doe')
  })
});