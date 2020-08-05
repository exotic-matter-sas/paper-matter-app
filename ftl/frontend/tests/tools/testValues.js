/*
 * Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
 * Licensed under the BSL License. See LICENSE in the project root for license information.
 */

// Mocked Vue props

export const ACCOUNT_PROPS = {
  account: { name: "Jon Snow" },
};

export const FOLDER_PROPS = {
  id: 1234,
  name: "Folder title",
  created: new Date("2019-04-18T10:59:00").toString(),
  parent: null,
};

export const FOLDER_PROPS_VARIANT = {
  id: 5678,
  name: "Folder title 2",
  parent: null,
};

export const FOLDER_PROPS_WITH_PARENT = {
  id: 1234,
  name: "Folder title",
  parent: "4321",
};

export const FOLDER_TREE_ITEM = {
  id: 1234,
  name: "Folder title",
  created: new Date("2019-04-18T10:59:00").toString(),
  has_descendant: false,
};

export const FOLDER_TREE_ITEM_WITH_DESCENDANT = {
  id: 1234,
  name: "Folder title",
  created: new Date("2019-04-18T10:59:00").toString(),
  has_descendant: true,
};

export const DOCUMENT_PROPS = {
  pid: "1000",
  title: "Document title",
  note: "Document note",
  created: new Date("2019-04-18T10:59:00").toString(),
  thumbnail_available: true,
  ftl_folder: null,
  path: [],
  download_url: "app/uploads/1000",
};

export const DOCUMENT_PROPS_VARIANT = {
  pid: "1001",
  title: "Document title 2",
  note: "Document note 2",
  created: new Date("2019-04-18T11:00:00").toString(),
  thumbnail_available: true,
  ftl_folder: null,
  path: [],
};

export const DOCUMENT_PROPS_WITH_FOLDER = {
  pid: "2000",
  title: "Document title",
  note: "Document note",
  created: new Date("2019-04-18T10:59:00").toString(),
  thumbnail_available: true,
  ftl_folder: 123,
  path: [],
};

export const DOCUMENT_PROPS_WITH_FOLDER_MOVED = {
  ftl_folder: 321,
  ...DOCUMENT_PROPS_WITH_FOLDER,
};

export const DOCUMENT_NO_THUMB_PROPS = {
  pid: "3000",
  title: "Document title",
  note: "Document note",
  created: new Date("2019-04-18T10:59:00").toString(),
  thumbnail_available: false,
  path: [],
  type: "application/pdf",
};

export const DOCUMENT_NO_THUMB_PROPS_2 = {
  pid: "3001",
  title: "Document title 2",
  note: "Document note 2",
  created: new Date("2019-04-18T10:59:00").toString(),
  thumbnail_available: false,
  path: [],
  type: "application/pdf",
};

export const DOCUMENT_SHARE_LINK = {
  pid: "s1000",
  created: "2020-07-27T12:40:43.000000Z",
  edited: "2020-07-27T12:40:43.000000Z",
  expire_at: null,
  note: "Share link note",
  public_url: ".../app/share/s1000",
};

export const DOCUMENT_SHARE_LINK_VARIANT = {
  pid: "s1001",
  created: "2020-07-27T12:40:44.000000Z",
  edited: "2020-07-27T12:40:44.000000Z",
  expire_at: null,
  note: "Share link note 2",
  public_url: ".../app/share/s1001",
};

export const FILES_PROPS = {
  name: 'test.pdf',
  path: 'absolute/path/test.pdf',
  webkitRelativePath: 'relative/path/test.pdf',
  type: 'application/pdf',
  lastModified: 1567521895187,
};

export const FILES_PROPS_2 = {
  name: 'test.txt',
  path: 'absolute/path/test.txt',
  webkitRelativePath: 'relative/path/test.txt',
  type: 'text/plain',
  lastModified: 1567521895188,
};

export const FILES_PROPS_3 = {
  name: 'test.DOC',
  path: 'absolute/path/test.DOC',
  webkitRelativePath: 'relative/path/test.DOC',
  type: 'application/msword',
  lastModified: 1567521895189,
};
