import App from "../../src/App";
import {createLocalVue, shallowMount} from "@vue/test-utils";
import BootstrapVue from "bootstrap-vue";
import {mixinAlert} from "../../src/vueMixins";

const localVue = createLocalVue();
localVue.use(BootstrapVue); // to avoid warning on tests execution
localVue.prototype.$_ = (text) => { return text; }; // i18n mock
localVue.mixin({methods: {mixinAlert}}); // set mixinAlert as set in main.js

const mockedUpdateFolder = jest.fn();
const mockedUpdateDocument = jest.fn();
const mockedChangeFolder = jest.fn();
const mockedToast = jest.fn();


describe('vue mixins call proper methods', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = shallowMount(App, {
      localVue,
      methods: {
        changeFolder: mockedChangeFolder,
        updateDocuments: mockedUpdateDocument,
        updateFolders: mockedUpdateFolder,
      }
    });
  });

  it('mixinAlert call bootstrapVue toast method', () => {
    //when
    wrapper.vm.$bvToast.toast = mockedToast.bind(wrapper.vm.$bvToast);
    wrapper.vm.mixinAlert('OK');

    //then
    expect(mockedToast).toHaveBeenCalled();
  })
});
