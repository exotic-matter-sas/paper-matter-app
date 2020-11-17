/*
 * Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
 * Licensed under the Business Source License. See LICENSE at project root for more information.
 */

import { createLocalVue, shallowMount } from "@vue/test-utils";

import axios from "axios";
import BootstrapVue from "bootstrap-vue";
import flushPromises from "flush-promises"; // needed for async tests

import * as tv from "./../tools/testValues.js";
import { axiosConfig } from "../../src/constants";

import FTLMoveFolder from "../../src/components/FTLMoveFolder";

const localVue = createLocalVue();

localVue.use(BootstrapVue); // avoid bootstrap vue warnings
localVue.component("font-awesome-icon", jest.fn()); // avoid font awesome warnings

localVue.prototype.$t = (text, args) => {
  return text + " " + args;
}; // i18n mock
localVue.prototype.$tc = (text, args = "") => {
  return text + args;
}; // i18n mock
localVue.prototype.$moment = () => {
  return { fromNow: jest.fn() };
}; // moment mock
localVue.prototype.$router = { push: jest.fn() }; // router mock
const mockedMixinAlert = jest.fn();
localVue.mixin({ methods: { mixinAlert: mockedMixinAlert } }); // mixinAlert mock

// mock calls to api requests
jest.mock("axios", () => ({
  patch: jest.fn(),
}));

const mockedMoveFolderResponse = {
  data: tv.FOLDER_PROPS_WITH_PARENT,
  status: 200,
};

const mockedSelectedMoveTargetFolder = jest.fn();

const folderProps = tv.FOLDER_PROPS;

describe("Component template", () => {
  let wrapper;
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(FTLMoveFolder, {
      localVue,
      propsData: {
        folder: folderProps,
      },
      computed: {
        selectedMoveTargetFolder: mockedSelectedMoveTargetFolder,
      },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("renders properly template text", async () => {
    expect(wrapper.text()).toContain("No folder selected");
  });

  it("renders properly html element", () => {
    const elementSelector = "#modal-move-folder";
    const elem = wrapper.find(elementSelector);
    expect(elem.is(elementSelector)).toBe(true);
  });
});

describe("FTLMoveFolder computed", () => {
  let wrapper;

  it("selectedMoveTargetFolder return value from $store", () => {
    // TODO test call to vuex store here
  });
});

describe("Component methods call api", () => {
  let wrapper;
  beforeEach(() => {
    axios.patch.mockResolvedValue(mockedMoveFolderResponse);
    mockedSelectedMoveTargetFolder.mockReturnValue(tv.FOLDER_PROPS_VARIANT);

    wrapper = shallowMount(FTLMoveFolder, {
      localVue,
      propsData: { folder: folderProps },
      computed: {
        selectedMoveTargetFolder: mockedSelectedMoveTargetFolder,
      },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("moveFolder call api", async () => {
    // when
    wrapper.vm.moveFolder();

    // then
    expect(axios.patch).toHaveBeenCalledWith(
      "/app/api/v1/folders/" + folderProps.id,
      { parent: tv.FOLDER_PROPS_VARIANT.id },
      axiosConfig
    );
    expect(axios.patch).toHaveBeenCalledTimes(1);
  });
});

describe("Component methods error handling", () => {
  let wrapper;
  beforeEach(() => {
    axios.patch.mockRejectedValue("fakeError");
    mockedSelectedMoveTargetFolder.mockReturnValue(tv.FOLDER_PROPS_VARIANT);

    wrapper = shallowMount(FTLMoveFolder, {
      localVue,
      propsData: { folder: folderProps },
      computed: {
        selectedMoveTargetFolder: mockedSelectedMoveTargetFolder,
      },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("moveFolder call mixinAlert in case of error", async () => {
    // force an error

    // when
    wrapper.vm.moveFolder();
    await flushPromises();

    // then mixinAlert is called with proper message
    expect(mockedMixinAlert).toHaveBeenCalledTimes(1);
    expect(mockedMixinAlert.mock.calls[0][0]).toContain("move folder");
  });
});

describe("Event emitted by component", () => {
  let wrapper;
  beforeEach(() => {
    axios.patch.mockResolvedValue(mockedMoveFolderResponse);
    mockedSelectedMoveTargetFolder.mockReturnValue(tv.FOLDER_PROPS_VARIANT);

    wrapper = shallowMount(FTLMoveFolder, {
      localVue,
      propsData: { folder: folderProps },
      computed: {
        selectedMoveTargetFolder: mockedSelectedMoveTargetFolder,
      },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it("event-folder-moved emitted when calling moveFolder", async () => {
    const testedEvent = "event-folder-moved";

    // when
    wrapper.vm.moveFolder();
    await flushPromises();

    // then
    expect(wrapper.emitted(testedEvent)).toBeTruthy();
    expect(wrapper.emitted(testedEvent).length).toBe(1);
    expect(wrapper.emitted(testedEvent)[0]).toEqual([
      {
        folder: folderProps,
        target_folder: mockedSelectedMoveTargetFolder(),
      },
    ]);
  });
});
