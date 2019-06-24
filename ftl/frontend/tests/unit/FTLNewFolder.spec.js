import axios from "axios";
import * as tv from "../tools/testValues";
import {axiosConfig} from "@/constants";
import {createLocalVue, shallowMount} from "@vue/test-utils";
import FTLNewFolder from "@/components/FTLNewFolder";
import BootstrapVue from "bootstrap-vue";
import flushPromises from "flush-promises";


const localVue = createLocalVue();
localVue.use(BootstrapVue); // to avoid warning on tests execution
localVue.prototype.$_ = (text) => {
  return text;
}; // i18n mock
localVue.prototype.$moment = () => {
  return {fromNow: jest.fn()}
};
localVue.prototype.$router = {push: jest.fn()}; // router mock
localVue.mixin({methods: {mixinAlert: jest.fn()}}); // mixin alert

jest.mock('axios', () => ({
  get: jest.fn(),
  post: jest.fn()
}));

const mockedPostFolderResponse = {
  data: tv.FOLDER_PROPS,
  status: 200,
  config: axiosConfig
};

describe('New folder', () => {
  let wrapper;

  beforeEach(() => {
    wrapper = shallowMount(FTLNewFolder, {
        localVue,
        methods: {}
      }
    );
  });

  it('createNewFolder call api', async () => {
    axios.post.mockResolvedValue(mockedPostFolderResponse);
    wrapper.setData({newFolderName: tv.FOLDER_PROPS.name});

    // when
    wrapper.vm.createNewFolder();
    await flushPromises();

    // then
    expect(axios.post).toHaveBeenCalledWith(
      '/app/api/v1/folders/',
      {name: tv.FOLDER_PROPS.name},
      axiosConfig
    );

    expect(wrapper.emitted('event-folder-created')).toBeTruthy();
  });
});
