import { createLocalVue, mount } from '@vue/test-utils';

import axios from 'axios';
import BootstrapVue from "bootstrap-vue";

import * as tv from './../tools/testValues.js'
import FTLViewDocumentPanel from "../../src/components/FTLViewDocumentPanel";

const localVue = createLocalVue();
localVue.use(BootstrapVue); // to avoid warning on tests execution

jest.mock('axios', () => ({
  delete: jest.fn()
}));


describe('FTLViewDocumentPanel template', () => {
  it('renders properly document details', () => {
    const wrapper = mount(FTLViewDocumentPanel, {
      localVue,
      propsData: { pid: tv.DOCUMENT_PROPS.pid }
    });
    expect(wrapper.html()).toContain(tv.DOCUMENT_PROPS.pid)
  });
});

// TODO once https://gitlab.com/exotic-matter/ftl-app/merge_requests/23 is merge
// merge master in this branche and retest test above