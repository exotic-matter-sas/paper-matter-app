import {createLocalVue, shallowMount} from '@vue/test-utils';
import axios from 'axios';
import BootstrapVue from "bootstrap-vue";
import * as tv from './../tools/testValues.js'
import FTLUpload from "../../src/components/FTLUpload";
import flushPromises from 'flush-promises';
import {axiosConfig} from "../../src/constants";
import {createThumbFromFile} from '../../src/thumbnailGenerator'

const localVue = createLocalVue();
localVue.use(BootstrapVue); // to avoid warning on tests execution
localVue.prototype.$_ = (text) => {
  return text;
}; // i18n mock
localVue.prototype.$moment = jest.fn();
localVue.mixin({methods: {mixinAlert: jest.fn()}}); // mixin alert

jest.mock('axios', () => ({
  post: jest.fn()
}));

jest.mock('../../src/thumbnailGenerator', () => ({
  createThumbFromFile: jest.fn()
}));

describe('FTLUpload template', () => {
  const wrapper = shallowMount(FTLUpload, {
    localVue,
    propsData: {currentFolder: tv.FOLDER_PROPS}
  });

  it('renders properly upload UI', () => {
    expect(wrapper.html()).toContain('Upload document')
  });
});

describe('FTLUpload script', () => {
  let axios_upload_conf;
  const mockedPostResponse = {
    data: {},
    status: 201,
    config: axiosConfig
  };
  let formData = new FormData();
  formData.append('thumbnail', 'base64str');
  formData.append('file', null);
  formData.append('json', JSON.stringify({'ftl_folder': tv.FOLDER_PROPS.id}));
  let wrapper;
  let upload_button;

  beforeEach(() => {
    axios.post.mockResolvedValue(mockedPostResponse);
    createThumbFromFile.mockResolvedValue("base64str");

    wrapper = shallowMount(FTLUpload, {
      localVue,
      propsData: {currentFolder: tv.FOLDER_PROPS},
    });
    axios_upload_conf = {
      onUploadProgress: wrapper.vm.refreshUploadProgression
    };
    Object.assign(axios_upload_conf, axiosConfig); // merge upload specific conf with generic crsf conf
    upload_button = wrapper.find('#upload-button');
  });

  it('uploadDocument call api', async () => {
    // when
    wrapper.vm.uploadDocument();

    await flushPromises();
    // then
    expect(axios.post).toHaveBeenCalledWith(
      '/app/api/v1/documents/upload',
      formData,
      axios_upload_conf
    );
  });
  it('uploadDocument call createThumbFromFile', async () => {
    // when
    wrapper.vm.uploadDocument();

    await flushPromises();
    // then
    expect(createThumbFromFile).toHaveBeenCalled()
  });
  it('uploadDocument emit event-new-upload', async () => {
    // when
    wrapper.vm.uploadDocument();

    await flushPromises();
    // then
    expect(wrapper.emitted('event-new-upload')).toBeTruthy();
  });
});
