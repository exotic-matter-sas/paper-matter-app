/*
 * Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
 * Licensed under the Business Source License. See LICENSE at project root for more information.
 */

import { createLocalVue, shallowMount } from "@vue/test-utils";
import FTLDeleteDocuments from "@/components/FTLDeleteDocuments";
import BootstrapVue from "bootstrap-vue";
import * as tv from "../tools/testValues";
import axios from "axios";
import { axiosConfig } from "@/constants";

const localVue = createLocalVue();
localVue.use(BootstrapVue); // avoid bootstrap vue warnings
localVue.component("font-awesome-icon", jest.fn()); // avoid font awesome warnings

// Mock prototype and mixin bellow
localVue.prototype.$t = (text, args = "") => {
  return text + args;
}; // i18n mock
localVue.prototype.$tc = (text, args = "") => {
  return text + args;
}; // i18n mock
localVue.prototype.$moment = () => {
  return { fromNow: jest.fn() };
}; // moment mock
localVue.prototype.$store = { commit: jest.fn() }; // vuex mock
const mockedMixinAlert = jest.fn();
localVue.mixin({
  methods: {
    mixinAlert: mockedMixinAlert,
    mixinAlertWarning: mockedMixinAlert,
  },
}); // mixin alert

// mock calls to api requests
jest.mock("axios", () => ({
  delete: jest.fn(),
}));

const docsProp = [tv.DOCUMENT_PROPS, tv.DOCUMENT_PROPS_WITH_FOLDER];
const mockedDeletedDocument = {
  status: 204,
};

describe("FTLDeleteDocuments template", () => {
  let wrapper;
  beforeEach(() => {
    wrapper = shallowMount(FTLDeleteDocuments, {
      localVue,
      propsData: { docs: docsProp },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("renders proper template", () => {
    expect(wrapper.html()).toContain("Delete documents");
  });

  it("renders properly FTLDeleteDocuments data for 1 document", () => {
    // overwrite docs prop with only 1 doc
    wrapper.setData({ docs: [docsProp[0]] });

    expect(wrapper.html()).toContain(docsProp[0].title);
  });

  it("renders properly FTLDeleteDocuments data for several documents", () => {
    expect(wrapper.html()).toContain(docsProp.length);
  });
});

describe("FTLDeleteDocuments methods", () => {
  let wrapper;
  beforeEach(() => {
    axios.delete.mockResolvedValue(mockedDeletedDocument);
    wrapper = shallowMount(FTLDeleteDocuments, {
      localVue,
      propsData: { docs: docsProp },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("deleteDocuments call api", () => {
    // when
    wrapper.vm.deleteDocuments();

    // then
    expect(axios.delete).toHaveBeenCalledWith(
      "/app/api/v1/documents/" + docsProp[0].pid,
      {
        ...axiosConfig,
        docPid: docsProp[0].pid,
      }
    );
    expect(axios.delete).toHaveBeenCalledWith(
      "/app/api/v1/documents/" + docsProp[1].pid,
      {
        ...axiosConfig,
        docPid: docsProp[1].pid,
      }
    );
    expect(axios.delete).toHaveBeenCalledTimes(2);
  });
});
