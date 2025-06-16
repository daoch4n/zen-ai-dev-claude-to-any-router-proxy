# FilesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createFileFilesPost**](FilesApi.md#createFileFilesPost) | **POST** /files | Create File |
| [**createFileProviderV1FilesPost**](FilesApi.md#createFileProviderV1FilesPost) | **POST** /{provider}/v1/files | Create File |
| [**createFileV1FilesPost**](FilesApi.md#createFileV1FilesPost) | **POST** /v1/files | Create File |
| [**deleteFileFilesFileIdDelete**](FilesApi.md#deleteFileFilesFileIdDelete) | **DELETE** /files/{file_id} | Delete File |
| [**deleteFileProviderV1FilesFileIdDelete**](FilesApi.md#deleteFileProviderV1FilesFileIdDelete) | **DELETE** /{provider}/v1/files/{file_id} | Delete File |
| [**deleteFileV1FilesFileIdDelete**](FilesApi.md#deleteFileV1FilesFileIdDelete) | **DELETE** /v1/files/{file_id} | Delete File |
| [**getFileContentFilesFileIdContentGet**](FilesApi.md#getFileContentFilesFileIdContentGet) | **GET** /files/{file_id}/content | Get File Content |
| [**getFileContentProviderV1FilesFileIdContentGet**](FilesApi.md#getFileContentProviderV1FilesFileIdContentGet) | **GET** /{provider}/v1/files/{file_id}/content | Get File Content |
| [**getFileContentV1FilesFileIdContentGet**](FilesApi.md#getFileContentV1FilesFileIdContentGet) | **GET** /v1/files/{file_id}/content | Get File Content |
| [**getFileFilesFileIdGet**](FilesApi.md#getFileFilesFileIdGet) | **GET** /files/{file_id} | Get File |
| [**getFileProviderV1FilesFileIdGet**](FilesApi.md#getFileProviderV1FilesFileIdGet) | **GET** /{provider}/v1/files/{file_id} | Get File |
| [**getFileV1FilesFileIdGet**](FilesApi.md#getFileV1FilesFileIdGet) | **GET** /v1/files/{file_id} | Get File |
| [**listFilesFilesGet**](FilesApi.md#listFilesFilesGet) | **GET** /files | List Files |
| [**listFilesProviderV1FilesGet**](FilesApi.md#listFilesProviderV1FilesGet) | **GET** /{provider}/v1/files | List Files |
| [**listFilesV1FilesGet**](FilesApi.md#listFilesV1FilesGet) | **GET** /v1/files | List Files |


<a name="createFileFilesPost"></a>
# **createFileFilesPost**
> oas_any_type_not_mapped createFileFilesPost(purpose, file, provider, target\_model\_names, custom\_llm\_provider)

Create File

    Upload a file that can be used across - Assistants API, Batch API  This is the equivalent of POST https://api.openai.com/v1/files  Supports Identical Params as: https://platform.openai.com/docs/api-reference/files/create  Example Curl &#x60;&#x60;&#x60; curl http://localhost:4000/v1/files         -H \&quot;Authorization: Bearer sk-1234\&quot;         -F purpose&#x3D;\&quot;batch\&quot;         -F file&#x3D;\&quot;@mydata.jsonl\&quot;  &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **purpose** | **String**|  | [default to null] |
| **file** | **File**|  | [default to null] |
| **provider** | **String**|  | [optional] [default to null] |
| **target\_model\_names** | **String**|  | [optional] [default to ] |
| **custom\_llm\_provider** | **String**|  | [optional] [default to openai] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: multipart/form-data
- **Accept**: application/json

<a name="createFileProviderV1FilesPost"></a>
# **createFileProviderV1FilesPost**
> oas_any_type_not_mapped createFileProviderV1FilesPost(provider, purpose, file, target\_model\_names, custom\_llm\_provider)

Create File

    Upload a file that can be used across - Assistants API, Batch API  This is the equivalent of POST https://api.openai.com/v1/files  Supports Identical Params as: https://platform.openai.com/docs/api-reference/files/create  Example Curl &#x60;&#x60;&#x60; curl http://localhost:4000/v1/files         -H \&quot;Authorization: Bearer sk-1234\&quot;         -F purpose&#x3D;\&quot;batch\&quot;         -F file&#x3D;\&quot;@mydata.jsonl\&quot;  &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **provider** | **String**|  | [default to null] |
| **purpose** | **String**|  | [default to null] |
| **file** | **File**|  | [default to null] |
| **target\_model\_names** | **String**|  | [optional] [default to ] |
| **custom\_llm\_provider** | **String**|  | [optional] [default to openai] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: multipart/form-data
- **Accept**: application/json

<a name="createFileV1FilesPost"></a>
# **createFileV1FilesPost**
> oas_any_type_not_mapped createFileV1FilesPost(purpose, file, provider, target\_model\_names, custom\_llm\_provider)

Create File

    Upload a file that can be used across - Assistants API, Batch API  This is the equivalent of POST https://api.openai.com/v1/files  Supports Identical Params as: https://platform.openai.com/docs/api-reference/files/create  Example Curl &#x60;&#x60;&#x60; curl http://localhost:4000/v1/files         -H \&quot;Authorization: Bearer sk-1234\&quot;         -F purpose&#x3D;\&quot;batch\&quot;         -F file&#x3D;\&quot;@mydata.jsonl\&quot;  &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **purpose** | **String**|  | [default to null] |
| **file** | **File**|  | [default to null] |
| **provider** | **String**|  | [optional] [default to null] |
| **target\_model\_names** | **String**|  | [optional] [default to ] |
| **custom\_llm\_provider** | **String**|  | [optional] [default to openai] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: multipart/form-data
- **Accept**: application/json

<a name="deleteFileFilesFileIdDelete"></a>
# **deleteFileFilesFileIdDelete**
> oas_any_type_not_mapped deleteFileFilesFileIdDelete(file\_id, provider)

Delete File

    Deletes a specified file. that can be used across - Assistants API, Batch API  This is the equivalent of DELETE https://api.openai.com/v1/files/{file_id}  Supports Identical Params as: https://platform.openai.com/docs/api-reference/files/delete  Example Curl &#x60;&#x60;&#x60; curl http://localhost:4000/v1/files/file-abc123     -X DELETE     -H \&quot;Authorization: Bearer $OPENAI_API_KEY\&quot;  &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **file\_id** | **String**|  | [default to null] |
| **provider** | **String**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="deleteFileProviderV1FilesFileIdDelete"></a>
# **deleteFileProviderV1FilesFileIdDelete**
> oas_any_type_not_mapped deleteFileProviderV1FilesFileIdDelete(file\_id, provider)

Delete File

    Deletes a specified file. that can be used across - Assistants API, Batch API  This is the equivalent of DELETE https://api.openai.com/v1/files/{file_id}  Supports Identical Params as: https://platform.openai.com/docs/api-reference/files/delete  Example Curl &#x60;&#x60;&#x60; curl http://localhost:4000/v1/files/file-abc123     -X DELETE     -H \&quot;Authorization: Bearer $OPENAI_API_KEY\&quot;  &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **file\_id** | **String**|  | [default to null] |
| **provider** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="deleteFileV1FilesFileIdDelete"></a>
# **deleteFileV1FilesFileIdDelete**
> oas_any_type_not_mapped deleteFileV1FilesFileIdDelete(file\_id, provider)

Delete File

    Deletes a specified file. that can be used across - Assistants API, Batch API  This is the equivalent of DELETE https://api.openai.com/v1/files/{file_id}  Supports Identical Params as: https://platform.openai.com/docs/api-reference/files/delete  Example Curl &#x60;&#x60;&#x60; curl http://localhost:4000/v1/files/file-abc123     -X DELETE     -H \&quot;Authorization: Bearer $OPENAI_API_KEY\&quot;  &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **file\_id** | **String**|  | [default to null] |
| **provider** | **String**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getFileContentFilesFileIdContentGet"></a>
# **getFileContentFilesFileIdContentGet**
> oas_any_type_not_mapped getFileContentFilesFileIdContentGet(file\_id, provider)

Get File Content

    Returns information about a specific file. that can be used across - Assistants API, Batch API  This is the equivalent of GET https://api.openai.com/v1/files/{file_id}/content  Supports Identical Params as: https://platform.openai.com/docs/api-reference/files/retrieve-contents  Example Curl &#x60;&#x60;&#x60; curl http://localhost:4000/v1/files/file-abc123/content         -H \&quot;Authorization: Bearer sk-1234\&quot;  &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **file\_id** | **String**|  | [default to null] |
| **provider** | **String**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getFileContentProviderV1FilesFileIdContentGet"></a>
# **getFileContentProviderV1FilesFileIdContentGet**
> oas_any_type_not_mapped getFileContentProviderV1FilesFileIdContentGet(file\_id, provider)

Get File Content

    Returns information about a specific file. that can be used across - Assistants API, Batch API  This is the equivalent of GET https://api.openai.com/v1/files/{file_id}/content  Supports Identical Params as: https://platform.openai.com/docs/api-reference/files/retrieve-contents  Example Curl &#x60;&#x60;&#x60; curl http://localhost:4000/v1/files/file-abc123/content         -H \&quot;Authorization: Bearer sk-1234\&quot;  &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **file\_id** | **String**|  | [default to null] |
| **provider** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getFileContentV1FilesFileIdContentGet"></a>
# **getFileContentV1FilesFileIdContentGet**
> oas_any_type_not_mapped getFileContentV1FilesFileIdContentGet(file\_id, provider)

Get File Content

    Returns information about a specific file. that can be used across - Assistants API, Batch API  This is the equivalent of GET https://api.openai.com/v1/files/{file_id}/content  Supports Identical Params as: https://platform.openai.com/docs/api-reference/files/retrieve-contents  Example Curl &#x60;&#x60;&#x60; curl http://localhost:4000/v1/files/file-abc123/content         -H \&quot;Authorization: Bearer sk-1234\&quot;  &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **file\_id** | **String**|  | [default to null] |
| **provider** | **String**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getFileFilesFileIdGet"></a>
# **getFileFilesFileIdGet**
> oas_any_type_not_mapped getFileFilesFileIdGet(file\_id, provider)

Get File

    Returns information about a specific file. that can be used across - Assistants API, Batch API  This is the equivalent of GET https://api.openai.com/v1/files/{file_id}  Supports Identical Params as: https://platform.openai.com/docs/api-reference/files/retrieve  Example Curl &#x60;&#x60;&#x60; curl http://localhost:4000/v1/files/file-abc123         -H \&quot;Authorization: Bearer sk-1234\&quot;  &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **file\_id** | **String**|  | [default to null] |
| **provider** | **String**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getFileProviderV1FilesFileIdGet"></a>
# **getFileProviderV1FilesFileIdGet**
> oas_any_type_not_mapped getFileProviderV1FilesFileIdGet(file\_id, provider)

Get File

    Returns information about a specific file. that can be used across - Assistants API, Batch API  This is the equivalent of GET https://api.openai.com/v1/files/{file_id}  Supports Identical Params as: https://platform.openai.com/docs/api-reference/files/retrieve  Example Curl &#x60;&#x60;&#x60; curl http://localhost:4000/v1/files/file-abc123         -H \&quot;Authorization: Bearer sk-1234\&quot;  &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **file\_id** | **String**|  | [default to null] |
| **provider** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getFileV1FilesFileIdGet"></a>
# **getFileV1FilesFileIdGet**
> oas_any_type_not_mapped getFileV1FilesFileIdGet(file\_id, provider)

Get File

    Returns information about a specific file. that can be used across - Assistants API, Batch API  This is the equivalent of GET https://api.openai.com/v1/files/{file_id}  Supports Identical Params as: https://platform.openai.com/docs/api-reference/files/retrieve  Example Curl &#x60;&#x60;&#x60; curl http://localhost:4000/v1/files/file-abc123         -H \&quot;Authorization: Bearer sk-1234\&quot;  &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **file\_id** | **String**|  | [default to null] |
| **provider** | **String**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="listFilesFilesGet"></a>
# **listFilesFilesGet**
> oas_any_type_not_mapped listFilesFilesGet(provider, target\_model\_names, purpose)

List Files

    Returns information about a specific file. that can be used across - Assistants API, Batch API  This is the equivalent of GET https://api.openai.com/v1/files/  Supports Identical Params as: https://platform.openai.com/docs/api-reference/files/list  Example Curl &#x60;&#x60;&#x60; curl http://localhost:4000/v1/files        -H \&quot;Authorization: Bearer sk-1234\&quot;  &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **provider** | **String**|  | [optional] [default to null] |
| **target\_model\_names** | **String**|  | [optional] [default to null] |
| **purpose** | **String**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="listFilesProviderV1FilesGet"></a>
# **listFilesProviderV1FilesGet**
> oas_any_type_not_mapped listFilesProviderV1FilesGet(provider, target\_model\_names, purpose)

List Files

    Returns information about a specific file. that can be used across - Assistants API, Batch API  This is the equivalent of GET https://api.openai.com/v1/files/  Supports Identical Params as: https://platform.openai.com/docs/api-reference/files/list  Example Curl &#x60;&#x60;&#x60; curl http://localhost:4000/v1/files        -H \&quot;Authorization: Bearer sk-1234\&quot;  &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **provider** | **String**|  | [default to null] |
| **target\_model\_names** | **String**|  | [optional] [default to null] |
| **purpose** | **String**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="listFilesV1FilesGet"></a>
# **listFilesV1FilesGet**
> oas_any_type_not_mapped listFilesV1FilesGet(provider, target\_model\_names, purpose)

List Files

    Returns information about a specific file. that can be used across - Assistants API, Batch API  This is the equivalent of GET https://api.openai.com/v1/files/  Supports Identical Params as: https://platform.openai.com/docs/api-reference/files/list  Example Curl &#x60;&#x60;&#x60; curl http://localhost:4000/v1/files        -H \&quot;Authorization: Bearer sk-1234\&quot;  &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **provider** | **String**|  | [optional] [default to null] |
| **target\_model\_names** | **String**|  | [optional] [default to null] |
| **purpose** | **String**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

