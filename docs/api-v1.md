Before you can query [Folders](#folders) and [Documents](#documents) resources, you have to obtain, store and manage an `access` and `refresh` token through [Authentication requests](#authentication).

## Authentication

### Get access and refresh tokens
**POST /api/token**

Generate an access and refresh token that follow the [JSON Web Token standard](https://en.wikipedia.org/wiki/JSON_Web_Token). You should store them for later use.

**Request body**

- **username** (used to login to your Paper Matter organization)
- **password** (used to login to your Paper Matter organization)

```json
{
    "username":"jon",
    "password": "KingInTheNorth!"
}
```

**Response** `200`

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTU2NjAzNzQ0MywianRpIjoiYjRlZjZmMjQzN2ZlNGI0MTlmYTEyNDI5YjhjNmFiNTEiLCJ1c2VyX2lkIjoxfQ.K89rsw1Nuo6jLffd73IJY0aHAXBOQK6kH4T6leV9uXM",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTY1OTUxOTQzLCJqdGkiOiI0NmMxZGNjODE2ZDY0NDAxOWM3MDY0OTc3MzIzNzU2NSIsInVzZXJfaWQiOjF9.WnehBvEklvXRV8sZyHbAdRgt8JUrsd9g2bt5npY4cyw"
}
```

 - `access` token should be passed inside the `Authorization` header for each authenticated request (eg. `Authorization: Bearer eyJ0eX...`)
 - `refresh` token should be used to get a fresh new access token after it expired after a short period (see [Refresh access token request](http://localhost:8001/api-v1/#refresh-access-token)).

**HTTP error status**

| Status | detail |
| ----- | ----- |
| 401 | No active account found with the given credentials |

### Refresh access token
**POST /api/token**

To use when the `access` token is expired or going to (eg. <1min), it return a fresh new access token to store in place of the previous one.

You can know when access token is about to expired by parsing the `exp` field inside the decoded access token (split the 3 parts on `.` and base64 url decode the 2nd part OR use a JWT lib to do it).

If the token is already expired all authenticated request will returns an `401` error (`{"code": "token_not_valid"}`).

Eventually the refresh token will also expired (after a longer period), if you're trying to refresh an expired refresh token a specific error will be returned. When it occurred you should recall [Get access token](#get-access-token) request and store new token values.

**Request body**

- **refresh** (`refresh` token given by [Get access token request](#get-access-token))

```json
{
    "refresh":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTU2NjAzNzczNywianRpIjoiNjYyYmI1NGQyYWJhNDAwY2E0ZDBhYTc0ZWFmYzc4OTciLCJ1c2VyX2lkIjoxfQ.nVC38rej3YwTn_4N8gKWcwzSx7HdSK6-r9BSOYixoTM"
}
```

**Response** `200`

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTY1OTYwODY4LCJqdGkiOiJmNjZjNWIzZDI0MmU0ZWVjOTc4OTgwNzZlZmVlNTAzMyIsInVzZXJfaWQiOjF9.FyhEl7ofgG2v91Id0QuBgKmISJ72k4K_09a8rSfT5Eo"
}
```

**HTTP error status**

| Status | detail | code |
| ----- | ----- | ----- |
| 401 | Token is invalid or expired | token_not_valid |

## Folders

### Create a folder
**POST /api/v1/folders**

**Request body**

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

| Status | detail | code |
| ----- | ----- | ----- |
| 400 | A folder with this name already exist | folder_name_unique_for_org_level |

### List folders
**GET /api/v1/folders**

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
**PATCH /api/v1/folders/`folder_id`**

Rename or move an existing folder.

**Request body** _(attributes omitted stay unchanged)_

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

| Status | detail | code |
| ----- | ----- | ----- |
| 400 | A folder can't be move inside one of its children | folder_parent_invalid |

### Delete a folder
**DELETE /api/v1/folders/`folder_id`**

**Response** `204`

## Documents

### Upload a document
**POST /api/v1/documents/upload**

**Request body** (`multipart/form-data`)

- **file**: PDF file binary
- _**json** (optional): additional data to set for document uploaded_
    - **ftl_folder**: parent folder id (if omitted or `null`, folder is created inside root folder)
- _**thumbnail** (optional): thumbnail to display in the documents list, thumbnail should be a PNG image encoded as data uri `data:image/png;base64,...` (if omitted thumbnail will be generated on next document display from web interface, recommended format is half the size of the original document)
non
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
  "pid": "f04be12a-b08d-4857-ade0-20c778a257b3",
  "title": "file.pdf",
  "note": "",
  "created": "2019-08-19T13:14:15.397396Z",
  "edited": "2019-08-19T13:14:15.408445Z",
  "ftl_folder": null,
  "thumbnail_available": false
}
```

**Specific error status**

| Status | detail | code |
| ----- | ----- | ----- |
| 400 | Specified ftl_folder doesn't exist | ftl_folder_not_found |

### List documents
**GET /api/v1/documents**

**Query strings params**

- _**flat** (optional): if present (no matter its value), all documents of the organization will be display_

OR

- _**search** (optional): a search query to filter all document of the organization_

OR

- _**level** (optional): the id of the folder to list (if omitted root folder is listed)_



**Response** `200`

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "pid": "4c092ae2-2c91-4759-9123-5f4af7538f85",
      "title": "file.pdf",
      "note": "",
      "created": "2019-08-19T15:03:03.504330Z",
      "edited": "2019-08-19T15:03:06.844287Z",
      "ftl_folder": null,
      "thumbnail_available": false
    },
    {
      "pid": "6d3a6286-7c1c-45f6-86c9-6452fa2928fa",
      "title": "file2.pdf",
      "note": "",
      "created": "2019-08-19T14:24:27.125753Z",
      "edited": "2019-08-19T14:24:30.431466Z",
      "ftl_folder": null,
      "thumbnail_available": false
    }
  ]
}
```
If there is too many results, results will be paginated. To get the next page results you have to repeat the request on the url specified in `next` field (or set an additional `page` query string with desired page number).

### Update a document
**PATCH /api/v1/documents/`document_pid`**

Rename, annotate, move a document (or set its thumbnail).

**Request body** _(attributes omitted stay unchanged)_

- _**title** (optional): document name string_
- _**note** (optional): document note string_
- _**ftl_folder** (optional): parent folder id (set to `null` to move to root folder)_
- _**thumbnail_binary** (optional): thumbnail to display in the documents list, thumbnail should be a PNG image encoded as data uri (`data:image/png;base64,...`)_

**Response** `200`

```json
{
  "pid": "4c092ae2-2c91-4759-9123-5f4af7538f85",
  "title": "renamed",
  "note": "",
  "created": "2019-08-19T15:03:03.504330Z",
  "edited": "2019-08-19T16:10:00.771661Z",
  "ftl_folder": null,
  "thumbnail_available": false
}
```

### Delete a document
**DELETE /api/v1/documents/`document_pid`**

**Response** `204`

## Tool to test API easily

1. Download and install [Insomnia](https://insomnia.rest/)

2. Download [API requests data](`insomnia.json`) (right click > save as...) and import them by clicking on the **Insomnia** main dropdown menu > **Import/export**

3. Open **Manage Environments** window using main dropdown menu (or **ctrl + E**)

4. Set `base_url`, `username` and `password` values in **Base Environment** (or create a private **Sub Environment** to override the default values, and **activate it** through the top left secondary dropdown menu)