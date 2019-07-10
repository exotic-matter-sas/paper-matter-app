// Mocked Vue props

export const ACCOUNT_PROPS = {
  account: {name: 'Jon Snow'}
};

export const FOLDER_PROPS = {
  id: '1234',
  name: 'Folder title',
  created: new Date('2019-04-18T10:59:00').toString(),
  parent: null,
};

export const FOLDER_PROPS_VARIANT = {
  id: '5678',
  name: 'Folder title 2',
  parent: null,
};

export const FOLDER_PROPS_WITH_PARENT = {
  id: '1234',
  name: 'Folder title',
  parent: '4321',
};

export const DOCUMENT_PROPS = {
  pid: '1234',
  title: 'Document title',
  note: 'Document note',
  created: new Date('2019-04-18T10:59:00').toString(),
  thumbnail_available: true
};

export const DOCUMENT_NO_THUMB_PROPS = {
  pid: '4321',
  title: 'Document title',
  note: 'Document note',
  created: new Date('2019-04-18T10:59:00').toString(),
  thumbnail_available: false
};

export const DOCUMENT_NO_THUMB_PROPS_2 = {
  pid: '8765',
  title: 'Document title 2',
  note: 'Document note 2',
  created: new Date('2019-04-18T10:59:00').toString(),
  thumbnail_available: false
};
