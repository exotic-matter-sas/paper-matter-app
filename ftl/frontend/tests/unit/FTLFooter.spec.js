/*
 * Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
 * Licensed under the Business Source License. See LICENSE at project root for more information.
 */

import { createLocalVue, shallowMount } from "@vue/test-utils";
import VueI18n from "vue-i18n";

import BootstrapVue from "bootstrap-vue";

import FTLFooter from "@/components/FTLFooter";

const localVue = createLocalVue();
localVue.use(BootstrapVue); // to avoid warning on tests execution
localVue.use(VueI18n);
localVue.prototype.$t = (text) => {
  return text;
}; // i18n mock
localVue.prototype.$tc = (text, args = "") => {
  return text + args;
}; // i18n mock

describe("FTLFooter template", () => {
  const wrapper = shallowMount(FTLFooter, {
    localVue: localVue,
  });

  it("renders properly footer content", () => {
    expect(wrapper.html()).toContain("<footer");
  });
});
