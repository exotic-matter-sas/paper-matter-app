# API V1 reference

_Before you can query the different resources, you have to obtain, store and manage an `access_token` and `refresh_token` as desbribed in [Authentication](#authentication)._

## Authentication

_The Paper Matter API uses the OAuth 2.0 protocol for authentication and authorization._

The following protocol endpoints are available:

 - Authorization page: `/oauth2/authorize/`
 - Get tokens endpoint: `/oauth2/token`
 - Revoke tokens endpoint: `/oauth2/revoke_token`

The following scopes are available: `read`, `write`.
 
Paper Matter supports the following OAuth 2.0 flows:

 - `Authorization Code` (`public` or `confidential`), recommended for most usage such as web app or native client
 - `Client Credentials`, only for trusted server side access

To access the API, you will need a set of `client_id` and `client_secret`:

 - For the instance we host (papermatter.app), please [contact us](https://welcome.papermatter.app/contact-us/) to
  apply for API access. 
 - For other instances, you have to ask instance admin to [generate those credentials inside the admin panel](`self-hosting.md#authorize-import-and-export-app-and-other-oauth2-apps`).

### Using Authorization Code flow

#### 1. Get authorization code

Open Paper Matter authorization page in user browser:

```text
https://[YOUR_PM_INSTANCE]/oauth2/authorize/
?response_type=code
&client_id=CLIENT_ID
&redirect_uri=https://my-site.example.org/callback
&scope=read
```
_User will be asked to login to Paper Matter and to authorize your app access to its account._ 

If authorization is successful, the given `redirect_uri` will be called by Paper Matter server with authorization code
inside a `code` querystring:

```text
https://my-site.example.org/callback?code=AUTHORIZATION_CODE
```

#### 2. Get tokens
**POST /oauth2/token**

**Request body** _([form url encoded](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST))_

- **client_id**: Oauth app `client_id`
- _**client_secret** (optional): Oauth app `client_secret`, can be omitted if app is `public`_
- **grant_type**: "authorization_code" or "client_credentials"
- **code**: Authorization `code` retrieved at previous step
- **redirect_uri**: `redirect_uri` used at previous step

```text
client_id=CLIENT_ID
&client_secret=CLIENT_SECRET
&grant_type=authorization_code
&code=AUTHORIZATION_CODE
&redirect_uri=https://my-site.example.org/callback
```

**Response** `200`

```json
{
  "access_token": "HhyHshfzszOIqApX3UEAdgqlcqgkbT",
  "expires_in": 36000,
  "token_type": "Bearer",
  "scope": "read",
  "refresh_token": "YoXmCNt19p6Ihlm1EIhCKzuB4UcuBF"
}
```

_`access_token` and `refresh_token` should be stored, they are required to call other requests, non-related to authentication._

- `access_token` have to be included inside `Authorization` HTTP header with the value `Bearer [access_token]`, this
 token will eventually expire as described below.
- `expires_in` is the `access_token` validity period in seconds, once expired authenticated request will return a code `403`. When this code is returned, you should use the [Refresh tokens request](#3-refresh-tokens) to get and store a new pair of tokens.
- `refresh_token` have to be used with [Refresh tokens request](#3-refresh-tokens), this token isn't limited to a validity period but is for single use.

#### 3. Refresh tokens

**POST /oauth2/token**

**Request body** _([form url encoded](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST))_

- **client_id**: Oauth app `client_id`
- _**client_secret** (optional): Oauth app `client_secret`, can be omitted if app is `public`_
- **grant_type**: "refresh_token"
- **refresh_token**: `refresh_token` retrieved at previous step

```text
client_id=CLIENT_ID
&client_secret=CLIENT_SECRET
&grant_type=refresh_token
&refresh_token=REFRESH_TOKEN
```

**Response** `200`

```json
{
  "access_token": "gGeae7urfUvC24YXrYtBGNbJuAC2yq",
  "expires_in": 36000,
  "token_type": "Bearer",
  "scope": "read",
  "refresh_token": "hdQtNwXo3PL6rD4Sp9kts5mDBDx622"
}
```

_News `access_token` and `refresh_token` should be stored in place of the old ones (reminder: the `refresh_token` expire
on use)._

#### 4. Revoke tokens

**POST /oauth2/revoke_token**

Revoke user authorization for your app.

**Request body** _([form url encoded](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST))_

- **client_id**: Oauth app `client_id`
- _**client_secret** (optional): Oauth app `client_secret`, can be omitted if app is `public`_
- **token**: `access_token` or `refresh_token`
- _**token_type_hint** (optional): "access_token" or "refresh_token", default to "access_token" if omitted_

```text
client_id=CLIENT_ID
&client_secret=CLIENT_SECRET
&token=ACCESS_TOKEN
```

**Response** `200`

_**Known bugs:**_

 - _If you revoke the `access_token` without revoking `refresh_token` and try to [Refresh tokens](#3-refresh-tokens)
an [error 500 will be raised](https://github.com/jazzband/django-oauth-toolkit/issues/839)_
 - _Revoking `refresh_token` only will also revoke user authorization for your app (so `access_token` wont be usable
 anymore)_

_So for now, until things get sorted out in [django-oauth-toolkit](https://github.com/jazzband/django-oauth-toolkit), we
recommend to revoke both tokens (`access_token` and then `refresh_token`), if you want to revoke user authorization for
your app._


## Folders

### Create a folder
**POST /app/api/v1/folders**

**Request body** _(JSON)_

- **name**: Folder name
- _**parent** (optional): parent folder id (if omitted or `null`, folder is created inside root folder_)

```json
{
    "name":"My folder name",
    "parent": 1
}
```

**Response** `201`

```json
{
  "id": 5,
  "name": "My folder name",
  "created": "2019-08-16T09:20:16.887929Z",
  "parent": 1,
  "paths": [
    {
      "id": 5,
      "name": "My folder name"
    }
  ],
  "has_descendant": false
}
```

**Specific error status**

| Status | details | code |
| ----- | ----- | ----- |
| 400 | A folder with this name already exist | folder_name_unique_for_org_level |

### List folders
**GET /app/api/v1/folders**

**Query strings params**

- _**level** (optional): the id of the folder to list (if omitted root folder is listed)_

**Response** `200`

```json
[
  {
    "id": 15,
    "name": "Folder 1",
    "created": "2019-08-16T16:03:39.985669Z",
    "parent": null,
    "paths": [
      {
        "id": 15,
        "name": "Folder 1"
      }
    ],
    "has_descendant": false
  },
  {
    "id": 19,
    "name": "Folder 2",
    "created": "2019-08-19T11:59:28.261624Z",
    "parent": null,
    "paths": [
      {
        "id": 19,
        "name": "Folder 2"
      }
    ],
    "has_descendant": false
  }
]
```

### Update a folders
**PATCH /app/api/v1/folders/`folder_id`**

Rename or move an existing folder.

**Request body** _(JSON, attributes omitted stay unchanged)_

- _**name** (optional): Folder name_
- _**parent** (optional): parent folder id (set to null to move to root folder)_

**Response** `200`

```json
{
  "id": 15,
  "name": "Folder 1 renamed",
  "created": "2019-08-16T16:03:39.985669Z",
  "parent": null,
  "paths": [
    {
      "id": 15,
      "name": "Folder 1 renamed"
    }
  ],
  "has_descendant": false
}
```

**Specific error status**

| Status | details | code |
| ----- | ----- | ----- |
| 400 | A folder can't be move inside one of its children | folder_parent_invalid |

### Delete a folder
**DELETE /app/api/v1/folders/`folder_id`**

**Response** `204`

## Documents

### Upload a document
**POST /app/api/v1/documents/upload**

**Request body** ([`multipart/form-data`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST))

- **file**: PDF file binary
- _**json** (optional): additional data to set for document uploaded_
    - **created**: creation date following ISO 8601 format, eg. `2019-11-18T00:42:42.242424Z` (if omitted or `null` current date will be set)
    - **ftl_folder**: parent folder id (if omitted or `null`, folder is created inside root folder)
    - **ignore_thumbnail_generation_error**: if set to `false` and sent **thumbnail** is corrupt or not properly formatted upload request will fail (if omitted or `true`, error will be ignored and document will be uploaded without thumbnail, it's the default behavior as some browsers may not support thumbnail generation using canvas)
    - **title**: document title, string (if omitted or `null`, file name will be used as document title)
    - **note**: document note, string (if omitted or `null`, no note will be set)
    - **md5**: document md5, it is recommended to provide this field for server to perform an integrity check to assert no corruption occurred during the upload process, a specific error is return on integrity check fail, string (if omitted or `null`, no integrity check is made)
- _**thumbnail** (optional): thumbnail to display in the documents list, thumbnail should be a PNG image encoded as data uri `data:image/png;base64,...` (if omitted thumbnail will be generated on next document display from web interface, recommended format is half the size of the original document)_
```
-----------------------------197247801933990060269089656
Content-Disposition: form-data; name="thumbnail"

data:image/png;base64,iVBORw0KGg...

-----------------------------197247801933990060269089656
Content-Disposition: form-data; name="file"; filename="file.pdf"
Content-Type: application/pdf

%PDF-1.4
%Ã¤Ã¼Ã¶Ã
2 0 obj...

-----------------------------197247801933990060269089656
Content-Disposition: form-data; name="json"

{}

-----------------------------197247801933990060269089656--
```

**Response** `201`

```json
{
  "pid":"f04be12a-b08d-4857-ade0-20c778a257b3",
  "title":"file",
  "note":"",
  "created":"2019-08-19T13:14:15.397396Z",
  "edited":"2019-08-19T13:14:15.408445Z",
  "ftl_folder":12,
  "thumbnail_available":false,
  "is_processed":true,
  "path":[
    {
      "id":34,
      "name":"a"
    },
    {
      "id":35,
      "name":"b"
    }
  ],
  "md5":"d85fce92a5789f66f58096402da6b98f",
  "size":123,
  "ocrized": true,
  "type": "application/pdf",
  "ext": ".pdf",
  "download_url": "app/uploads/f04be12a-b08d-4857-ade0-20c778a257b3"
}
```

**Specific error status**

| Status | details | code |
| ----- | ----- | ----- |
| 400 | Specified ftl_folder doesn't exist | ftl_folder_not_found |
| 400 | Document has been corrupted during upload, please retry | ftl_document_md5_mismatch |
| 415 | Unsupported document format | ftl_document_type_unsupported | 
| 400 | Missing parameter `file` or/and `json` in POST body | ftl_missing_file_or_json_in_body | 
| 400 | The file is empty | ftl_file_empty | 
| 400 | The thumbnail could not be decoded | ftl_thumbnail_generation_error | 

### List documents
**GET /app/api/v1/documents**

**Query strings params**

------------------------------------------------------------------------------------------------------------

- _**flat** (optional): if present (no matter its value), all documents of the organization will be display_

OR

- _**search** (optional): a search query to filter all document of the organization_

OR / AND (can be combined with `flat`)

- _**level** (optional): the id of the folder to list from (if omitted root folder is listed)_ 

------------------------------------------------------------------------------------------------------------

- _**ordering** (optional): specify the sort to apply to the documents list (if omitted AND **search** also omitted default value is `-created`, if omitted AND **search** present default value is `-rank`)._

    _Supported values are:_
  - _`created`: sort documents on their creation date, older first_
  - _`-created`: sort documents on their creation date, recent first_
  - _`title`: sort documents on their title by alphabetical order_
  - _`-title`: sort documents on their title by reverse alphabetical order_
  - _`-rank`: sort documents on their title, note and full text content by relevance against current **search** query_

**Response** `200`

```json
{
  "count":2,
  "next":null,
  "previous":null,
  "results":[
    {
      "pid":"4c092ae2-2c91-4759-9123-5f4af7538f85",
      "title":"file",
      "note":"",
      "created":"2019-08-19T15:03:03.504330Z",
      "edited":"2019-08-19T15:03:06.844287Z",
      "ftl_folder":12,
      "thumbnail_available":true,
      "thumbnail_url": "/app/app/api/v1/documents/4c092ae2-2c91-4759-9123-5f4af7538f85/thumbnail.png",
      "is_processed":true,
      "path":[
        {
          "id":34,
          "name":"a"
        },
        {
          "id":35,
          "name":"b"
        }
      ],
      "md5":"d85fce92a5789f66f58096402da6b98f",
      "size":123,
      "ocrized": true,
      "type": "application/pdf",
      "ext": ".pdf",
      "download_url": "app/uploads/f04be12a-b08d-4857-ade0-20c778a257b3"
    },
    {
      "pid":"6d3a6286-7c1c-45f6-86c9-6452fa2928fa",
      "title":"file2.pdf",
      "note":"",
      "created":"2019-08-19T14:24:27.125753Z",
      "edited":"2019-08-19T14:24:30.431466Z",
      "ftl_folder":12,
      "thumbnail_available":false,
      "thumbnail_url": null,
      "is_processed":true,
      "path":[
        {
          "id":34,
          "name":"a"
        },
        {
          "id":35,
          "name":"b"
        }
      ],
      "md5":"d85fce92a5789f66f58096402da6b98f",
      "size":123,
      "ocrized": true,
      "type": "application/pdf",
      "ext": ".pdf",
      "download_url": "app/uploads/f04be12a-b08d-4857-ade0-20c778a257b3"
    }
  ]
}
```
If there is too many results, results will be paginated. To get the next page results you have to call the url specified in `next` field (or set an additional `page` query string with desired page number, page start at `1`).

### Get a document
**GET /app/api/v1/documents/`document_pid`**

**Response** `200`

```json
{
  "pid":"4c092ae2-2c91-4759-9123-5f4af7538f85",
  "title":"file",
  "note":"",
  "created":"2019-08-19T15:03:03.504330Z",
  "edited":"2019-08-19T15:03:06.844287Z",
  "ftl_folder":12,
  "thumbnail_available":false,
  "is_processed":true,
  "thumbnail_url": "/app/app/api/v1/documents/4c092ae2-2c91-4759-9123-5f4af7538f85/thumbnail.png",
  "path":[
    {
      "id":34,
      "name":"a"
    },
    {
      "id":35,
      "name":"b"
    }
  ],
  "md5":"d85fce92a5789f66f58096402da6b98f",
  "size":123,
  "ocrized": true,
  "type": "application/pdf",
  "ext": ".pdf",
  "download_url": "app/uploads/f04be12a-b08d-4857-ade0-20c778a257b3"
}
```
Return the same data than **List documents** request but for a single document.

### Download a document
**GET /app/api/v1/documents/`document_pid`/download**

**Response** `200`

```
%PDF-1.4
3 0 obj <<
...
%%EOF
```

### Update a document
**PATCH /app/api/v1/documents/`document_pid`**

Rename, annotate, move a document (or set its thumbnail).

**Request body** _(JSON, attributes omitted stay unchanged)_

- _**title** (optional): document name string_
- _**note** (optional): document note string_
- _**ftl_folder** (optional): parent folder id (set to `null` to move to root folder)_
- _**thumbnail_binary** (optional): thumbnail to display in the documents list, thumbnail should be a PNG image encoded as data uri (`data:image/png;base64,...`)_

**Response** `200`

```json
{
  "pid":"4c092ae2-2c91-4759-9123-5f4af7538f85",
  "title":"renamed",
  "note":"",
  "created":"2019-08-19T15:03:03.504330Z",
  "edited":"2019-08-19T16:10:00.771661Z",
  "ftl_folder":12,
  "thumbnail_available":false,
  "is_processed":true,
  "path":[
    {
      "id":34,
      "name":"a"
    },
    {
      "id":35,
      "name":"b"
    }
  ],
  "md5":"d85fce92a5789f66f58096402da6b98f",
  "size":123,
  "ocrized": true,
  "type": "application/pdf",
  "ext": ".pdf",
  "download_url": "app/uploads/f04be12a-b08d-4857-ade0-20c778a257b3"
}
```

### Delete a document
**DELETE /app/api/v1/documents/`document_pid`**

**Response** `204`

## Documents share links

### Add a document share link
**POST /app/api/v1/documents/`document_pid`/share**

**Request body** _(JSON)_

- _**expire_at** (optional): an expiration date, following ISO 8601 format, eg. `2019-11-18T00:42:42.242424Z`_
- _**note** (optional): document share link note, string_

**Response** `201`

```json
{
  "pid": "7468babe-6e5e-4e9f-809b-c20758ee47ed",
  "created": "2020-07-24T14:38:39.535580Z",
  "edited": "2020-07-24T14:38:39.536544Z",
  "expire_at": null,
  "note": "",
  "public_url": ".../app/share/7468babe-6e5e-4e9f-809b-c20758ee47ed"
}
```

### List document share links
**GET /app/api/v1/documents/`document_pid`/share**

**Response** `200`

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "pid": "28005874-a495-4d08-b2ae-4ebc5ec8f212",
      "created": "2020-07-24T14:44:19.472368Z",
      "edited": "2020-07-24T14:44:19.472560Z",
      "expire_at": null,
      "note": "",
      "public_url": ".../app/share/28005874-a495-4d08-b2ae-4ebc5ec8f212"
    },
    {
      "pid": "f9c61c7f-8ee7-4d4f-8fa7-5f3653853339",
      "created": "2020-07-24T14:44:11.728826Z",
      "edited": "2020-07-24T14:44:11.729134Z",
      "expire_at": null,
      "note": "",
      "public_url": ".../app/share/f9c61c7f-8ee7-4d4f-8fa7-5f3653853339"
    }
  ]
}
```
If there is too many results, results will be paginated. To get the next page results you have to call the url specified in `next` field (or set an additional `page` query string with desired page number, page start at `1`).

### Get a document share link
**GET /app/api/v1/documents/`document_pid`/share/`document_shared_link_pid`**

**Response** `200`

```json
{
  "pid": "28005874-a495-4d08-b2ae-4ebc5ec8f212",
  "created": "2020-07-24T14:44:19.472368Z",
  "edited": "2020-07-24T14:44:19.472560Z",
  "expire_at": null,
  "note": "",
  "public_url": ".../app/share/28005874-a495-4d08-b2ae-4ebc5ec8f212"
}
```
Return the same data than **List documents share links** request but for a single share link.

### Update a document share link
**PATCH /app/api/v1/documents/`document_pid`/share/`document_shared_link_pid`**

Update a document share link note or expiration date.

**Request body** _(JSON, attributes omitted stay unchanged)_

- _**expire_at** (optional): an expiration date, following ISO 8601 format, eg. `2019-11-18T00:42:42.242424Z`_
- _**note** (optional): document share link note string_

**Response** `200`

```json
{
  "pid": "28005874-a495-4d08-b2ae-4ebc5ec8f212",
  "created": "2020-07-24T14:44:19.472368Z",
  "edited": "2020-07-24T14:44:19.472560Z",
  "expire_at": null,
  "note": "",
  "public_url": ".../app/share/28005874-a495-4d08-b2ae-4ebc5ec8f212"
}
```

### Delete a document share link
**DELETE /app/api/v1/documents/`document_pid`/share/`document_shared_link_pid`**

**Response** `204`

## Tool to test API quickly

1. Download and install [Insomnia](https://insomnia.rest/)

2. Download [API requests data](`insomnia.json`) (right click > save as...) and import them by clicking on the **Insomnia** main dropdown menu > **Import/export**

3. Open **Manage Environments** window using main dropdown menu (or **ctrl + E**)

4. Set `base_url` (Paper Matter instance host name), `client_id`, `redirect_uri`, `grant_type`, `client_secret` and `authorization_code` values in **Base Environment** (or create a private **Sub Environment** to override the default values, and **activate it** through the top left secondary dropdown menu)