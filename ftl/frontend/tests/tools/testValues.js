// Mocked Vue props

export const ACCOUNT_PROPS = {
  account: {name: 'John Doe'}
};

export const FOLDER_PROPS = {
  id: '1234',
  name: 'Folder title',
};

export const FOLDER_PROPS_VARIANT = {
  id: '5678',
  name: 'Folder title 2',
};

export const DOCUMENT_PROPS = {
  pid: '1234',
  title: 'Document title',
  note: 'Document note',
  created: new Date('2019-04-18T10:59:00').toString()
};

// Mocked AXIOS generic conf

export const AXIOS_CRSF_CONF = {
    xsrfCookieName: 'csrftoken',
    xsrfHeaderName: 'X-CSRFToken'
};

