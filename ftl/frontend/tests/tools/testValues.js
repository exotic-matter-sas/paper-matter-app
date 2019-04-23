// Mocked Vue props

export const ACCOUNT_PROPS = {
  account: {name: 'John Doe'}
};

export const FOLDER_PROPS = {
  name: 'Folder title'
};

export const DOCUMENT_PROPS = {
  pid: '1234',
  title: 'Document title',
  note: 'Document note',
  created: new Date('2019-04-18T10:59:00').toString()
};

// Mocked AXIOS data

export const AXIOS_CONF = {
    xsrfCookieName: 'csrftoken',
    xsrfHeaderName: 'X-CSRFToken'
};

