import { createLocalVue, shallowMount } from '@vue/test-utils';

import axios from 'axios';
import BootstrapVue from "bootstrap-vue";

import * as tv from './../tools/testValues.js'
import FTLUpload from "../../src/components/FTLUpload";

const localVue = createLocalVue();
localVue.use(BootstrapVue); // to avoid warning on tests execution

jest.mock('axios', () => ({
  post: jest.fn()
}));


describe('FTLUpload template', () => {
  const wrapper = shallowMount(FTLUpload, {
    localVue,
    propsData: { currentFolder: tv.FOLDER_PROPS }
  });

  it('renders properly upload UI', () => {
    expect(wrapper.html()).toContain('Upload document')
  });
});

describe('FTLUpload script', () => {
  let axios_upload_conf;
  const mockedPostResponse  = {
    data: {},
    status: 201,
    config: tv.AXIOS_CRSF_CONF
  };
  let formData = new FormData();
  formData.append('file', null);
  formData.append('json', JSON.stringify({'ftl_folder': tv.FOLDER_PROPS.id}));
  let wrapper;
  let upload_button;

  beforeEach(() => {
    axios.post.mockResolvedValue(mockedPostResponse);
    wrapper = shallowMount(FTLUpload, {
      localVue,
      propsData: { currentFolder: tv.FOLDER_PROPS }
    });
    axios_upload_conf = {
      onUploadProgress: wrapper.vm.refreshUploadProgression
    };
    Object.assign(axios_upload_conf, tv.AXIOS_CRSF_CONF); // merge upload specific conf with generic crsf conf
    upload_button = wrapper.find('#upload-button');
  });

  it('uploadDocument call api', () => {
    // when
    wrapper.vm.uploadDocument();

    // then
    expect(axios.post).toHaveBeenCalledWith(
        '/app/api/v1/documents/upload',
        formData,
        axios_upload_conf
    );
  });
  it('uploadDocument emit event-delete-doc', done => {
    // when
    wrapper.vm.uploadDocument();

    // then
    wrapper.vm.$nextTick(() => {
      expect(wrapper.emitted('event-new-upload')).toBeTruthy();
      done();
    });
  });
});
