/*
 * Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
 * Licensed under the BSL License. See LICENSE in the project root for license information.
 */

import { createLocalVue, shallowMount } from "@vue/test-utils";

import BootstrapVue from "bootstrap-vue";

import * as tv from "./../tools/testValues.js";
import FTLFolder from "../../src/components/FTLFolder";
import flushPromises from "flush-promises";

const localVue = createLocalVue();
localVue.use(BootstrapVue); // to avoid warning on tests execution
localVue.prototype.$t = (text) => {
  return text;
}; // i18n mock
localVue.prototype.$tc = (text, args = "") => {
  return text + args;
}; // i18n mock
localVue.prototype.$moment = () => {
  return { fromNow: jest.fn() };
};

describe("FTLFolder template", () => {
  let wrapper;
  beforeEach(() => {
    wrapper = shallowMount(FTLFolder, {
      localVue,
      propsData: { folder: tv.FOLDER_PROPS },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("renders properly folder data", () => {
    expect(wrapper.html()).toContain(tv.FOLDER_PROPS.name);
  });
});

describe("FTLFolder methods", () => {
  let wrapper;
  beforeEach(() => {
    wrapper = shallowMount(FTLFolder, {
      localVue,
      propsData: { folder: tv.FOLDER_PROPS },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("navigate set navigating true", () => {
    // given
    wrapper.setData({ navigating: false });

    // when
    wrapper.vm.navigate();

    // then
    expect(wrapper.vm.navigating).toEqual(true);
  });

  it("navigate emit event-change-folder", async () => {
    const testedEvent = "event-change-folder";

    // when
    wrapper.vm.navigate();
    await flushPromises();

    // then
    expect(wrapper.emitted(testedEvent)).toBeTruthy();
    expect(wrapper.emitted(testedEvent).length).toBe(1);
    expect(wrapper.emitted(testedEvent)[0]).toEqual([tv.FOLDER_PROPS]);
  });
});
