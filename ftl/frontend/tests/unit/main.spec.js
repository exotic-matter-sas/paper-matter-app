/*
 * Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
 * Licensed under the Business Source License. See LICENSE at project root for more information.
 */

import App from "../../src/App";
import { createLocalVue, shallowMount } from "@vue/test-utils";
import BootstrapVue from "bootstrap-vue";
import { mixinAlert, mixinAlertWarning } from "../../src/vueMixins";
import VueRouter from "vue-router";

const localVue = createLocalVue();
localVue.use(BootstrapVue); // to avoid warning on tests execution
localVue.use(VueRouter);
localVue.prototype.$t = (text) => {
  return text;
}; // i18n mock
localVue.prototype.$tc = (text, args = "") => {
  return text + args;
}; // i18n mock
localVue.prototype.$moment = () => {
  return { fromNow: jest.fn() };
};
localVue.mixin({ methods: { mixinAlert, mixinAlertWarning } }); // set mixinAlert as set in main.js

const mockedUpdateFolder = jest.fn();
const mockedUpdateDocument = jest.fn();
const mockedChangeFolder = jest.fn();
const mockedToast = jest.fn();

describe("vue mixins call proper methods", () => {
  let wrapper;
  beforeEach(() => {
    wrapper = shallowMount(App, {
      localVue,
      methods: {
        changeFolder: mockedChangeFolder,
        updateDocuments: mockedUpdateDocument,
        updateFolders: mockedUpdateFolder,
      },
    });
  });

  it("mixinAlert and mixinAlertWarning call bootstrapVue toast method", () => {
    //when
    wrapper.vm.$root.$bvToast.toast = mockedToast.bind(
      wrapper.vm.$root.$bvToast
    );
    wrapper.vm.mixinAlert("OK");
    wrapper.vm.mixinAlertWarning("OK");

    //then
    expect(mockedToast).toHaveBeenCalledTimes(2);
  });
});
