/*
 * Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
 * Licensed under the BSL License. See LICENSE in the project root for license information.
 */

import {createLocalVue, shallowMount} from '@vue/test-utils';

import axios from 'axios';
import BootstrapVue from "bootstrap-vue";
import flushPromises from "flush-promises"; // needed for async tests
import * as tv from './../tools/testValues.js'
import {axiosConfig} from "../../src/constants";
import marked from "marked";
import dompurify from "dompurify";

import FTLNote from "../../src/components/FTLNote";
import {markedConfig} from "@/constants";

// Create clean Vue instance and set installed package to avoid warning
const localVue = createLocalVue();
localVue.use(BootstrapVue); // avoid bootstrap vue warnings
localVue.component('font-awesome-icon', jest.fn()); // avoid font awesome warnings

// Mock prototype and mixin bellow
localVue.prototype.$t = (text, args = '') => {
  return text + args
};// i18n mock
localVue.prototype.$tc = (text, args='') => {return text + args};// i18n mock
localVue.prototype.$moment = () => {
  return {fromNow: jest.fn()}
}; // moment mock
const mockedMixinAlert = jest.fn();
localVue.mixin({methods: {mixinAlert: mockedMixinAlert}}); // mixinAlert mock

// mock calls to api requests
jest.mock('axios', () => ({
  patch: jest.fn(),
}));
// mock calls to markdown and html sanitize library
jest.mock('marked', () => jest.fn());
jest.mock('dompurify', () => ({
  sanitize: jest.fn(),
}));

const mockedGetNoteMarkdownSanitized = jest.fn();

const mockedPatchDocument = {
  data: tv.DOCUMENT_PROPS,
  status: 200
};

const docProp = tv.DOCUMENT_PROPS;

describe('FTLNote template', () => {
  let wrapper;
  beforeEach(() => {
    mockedGetNoteMarkdownSanitized.mockReturnValue(docProp.note);
    wrapper = shallowMount(FTLNote, {
      localVue,
      computed: {getNoteMarkdownSanitized: mockedGetNoteMarkdownSanitized},
      propsData: {doc: docProp}
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('renders properly FTLNote data', () => {
    expect(wrapper.html()).toContain(docProp.note);
  });
});

describe('FTLNote computed', () => {
  let wrapper;
  const mockedMarkdownToHtmlValue = '<h1>titre 1</h1>';
  const mockedSanitizeValue = '<h1>titre 1 sanitized</h1>';
  beforeEach(() => {
    marked.mockReturnValue(mockedMarkdownToHtmlValue);
    dompurify.sanitize.mockReturnValue(mockedSanitizeValue);
    wrapper = shallowMount(FTLNote, {
      localVue,
      propsData: {doc: docProp}
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('getNoteMarkdownSanitized properly call markdown and html sanitize library', () => {
    const markdownToConvertAndSanitize = '# titre 1';
    wrapper.setData({text: markdownToConvertAndSanitize});

    // when
    const testedValue = wrapper.vm.getNoteMarkdownSanitized;

    expect(marked).toBeCalledWith(markdownToConvertAndSanitize, markedConfig);
    expect(dompurify.sanitize).toBeCalledWith(mockedMarkdownToHtmlValue);
    expect(testedValue).toEqual(mockedSanitizeValue);
  });
});

describe('FTLNote methods', () => {
  let wrapper;
  beforeEach(() => {
    axios.patch.mockResolvedValue(mockedPatchDocument);
    wrapper = shallowMount(FTLNote, {
      localVue,
      propsData: {doc: docProp}
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('updateNote call api', () => {
    wrapper.setData({text: "new note"});
    // when
    wrapper.vm.updateNote();

    // then
    expect(axios.patch).toHaveBeenCalledWith('/app/api/v1/documents/' + docProp.pid, {note: "new note"}, axiosConfig);
    expect(axios.patch).toHaveBeenCalledTimes(1);
  });

  it('updateNote emit event event-document-note-edited', async () => {
    const testedEvent = 'event-document-note-edited';

    // when
    wrapper.vm.updateNote();
    await flushPromises();

    // then
    expect(wrapper.emitted(testedEvent)).toBeTruthy();
    expect(wrapper.emitted(testedEvent).length).toBe(1);
    expect(wrapper.emitted(testedEvent)[0]).toEqual([{doc: mockedPatchDocument.data}])
  });

  it('updateNote call mixinAlert in case of API error', async () => {
    axios.patch.mockRejectedValue('errorDescription');

    // when
    wrapper.vm.updateNote();
    await flushPromises();

    // then
    expect(mockedMixinAlert).toHaveBeenCalledTimes(1);
    expect(mockedMixinAlert.mock.calls[0][0]).toContain('Could not save note');
  });

  it('cancelUpdate set values', () => {
    wrapper.setData({
      editing: true,
      text: 'updated note'
    });

    // when
    wrapper.vm.cancelUpdate();

    // then
    expect(wrapper.vm.editing).toBe(false);
    expect(wrapper.vm.text).toEqual(docProp.note);
  });
});
