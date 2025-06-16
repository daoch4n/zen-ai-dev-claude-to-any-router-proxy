# BatchApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**cancelBatchBatchesBatchIdCancelPost**](BatchApi.md#cancelBatchBatchesBatchIdCancelPost) | **POST** /batches/{batch_id}/cancel | Cancel Batch |
| [**cancelBatchProviderV1BatchesBatchIdCancelPost**](BatchApi.md#cancelBatchProviderV1BatchesBatchIdCancelPost) | **POST** /{provider}/v1/batches/{batch_id}/cancel | Cancel Batch |
| [**cancelBatchV1BatchesBatchIdCancelPost**](BatchApi.md#cancelBatchV1BatchesBatchIdCancelPost) | **POST** /v1/batches/{batch_id}/cancel | Cancel Batch |
| [**createBatchBatchesPost**](BatchApi.md#createBatchBatchesPost) | **POST** /batches | Create Batch |
| [**createBatchProviderV1BatchesPost**](BatchApi.md#createBatchProviderV1BatchesPost) | **POST** /{provider}/v1/batches | Create Batch |
| [**createBatchV1BatchesPost**](BatchApi.md#createBatchV1BatchesPost) | **POST** /v1/batches | Create Batch |
| [**listBatchesBatchesGet**](BatchApi.md#listBatchesBatchesGet) | **GET** /batches | List Batches |
| [**listBatchesProviderV1BatchesGet**](BatchApi.md#listBatchesProviderV1BatchesGet) | **GET** /{provider}/v1/batches | List Batches |
| [**listBatchesV1BatchesGet**](BatchApi.md#listBatchesV1BatchesGet) | **GET** /v1/batches | List Batches |
| [**retrieveBatchBatchesBatchIdGet**](BatchApi.md#retrieveBatchBatchesBatchIdGet) | **GET** /batches/{batch_id} | Retrieve Batch |
| [**retrieveBatchProviderV1BatchesBatchIdGet**](BatchApi.md#retrieveBatchProviderV1BatchesBatchIdGet) | **GET** /{provider}/v1/batches/{batch_id} | Retrieve Batch |
| [**retrieveBatchV1BatchesBatchIdGet**](BatchApi.md#retrieveBatchV1BatchesBatchIdGet) | **GET** /v1/batches/{batch_id} | Retrieve Batch |


<a name="cancelBatchBatchesBatchIdCancelPost"></a>
# **cancelBatchBatchesBatchIdCancelPost**
> oas_any_type_not_mapped cancelBatchBatchesBatchIdCancelPost(batch\_id, provider)

Cancel Batch

    Cancel a batch. This is the equivalent of POST https://api.openai.com/v1/batches/{batch_id}/cancel  Supports Identical Params as: https://platform.openai.com/docs/api-reference/batch/cancel  Example Curl &#x60;&#x60;&#x60; curl http://localhost:4000/v1/batches/batch_abc123/cancel         -H \&quot;Authorization: Bearer sk-1234\&quot;         -H \&quot;Content-Type: application/json\&quot;         -X POST  &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **batch\_id** | **String**|  | [default to null] |
| **provider** | **String**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="cancelBatchProviderV1BatchesBatchIdCancelPost"></a>
# **cancelBatchProviderV1BatchesBatchIdCancelPost**
> oas_any_type_not_mapped cancelBatchProviderV1BatchesBatchIdCancelPost(batch\_id, provider)

Cancel Batch

    Cancel a batch. This is the equivalent of POST https://api.openai.com/v1/batches/{batch_id}/cancel  Supports Identical Params as: https://platform.openai.com/docs/api-reference/batch/cancel  Example Curl &#x60;&#x60;&#x60; curl http://localhost:4000/v1/batches/batch_abc123/cancel         -H \&quot;Authorization: Bearer sk-1234\&quot;         -H \&quot;Content-Type: application/json\&quot;         -X POST  &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **batch\_id** | **String**|  | [default to null] |
| **provider** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="cancelBatchV1BatchesBatchIdCancelPost"></a>
# **cancelBatchV1BatchesBatchIdCancelPost**
> oas_any_type_not_mapped cancelBatchV1BatchesBatchIdCancelPost(batch\_id, provider)

Cancel Batch

    Cancel a batch. This is the equivalent of POST https://api.openai.com/v1/batches/{batch_id}/cancel  Supports Identical Params as: https://platform.openai.com/docs/api-reference/batch/cancel  Example Curl &#x60;&#x60;&#x60; curl http://localhost:4000/v1/batches/batch_abc123/cancel         -H \&quot;Authorization: Bearer sk-1234\&quot;         -H \&quot;Content-Type: application/json\&quot;         -X POST  &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **batch\_id** | **String**|  | [default to null] |
| **provider** | **String**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="createBatchBatchesPost"></a>
# **createBatchBatchesPost**
> oas_any_type_not_mapped createBatchBatchesPost(provider)

Create Batch

    Create large batches of API requests for asynchronous processing. This is the equivalent of POST https://api.openai.com/v1/batch Supports Identical Params as: https://platform.openai.com/docs/api-reference/batch  Example Curl &#x60;&#x60;&#x60; curl http://localhost:4000/v1/batches         -H \&quot;Authorization: Bearer sk-1234\&quot;         -H \&quot;Content-Type: application/json\&quot;         -d &#39;{         \&quot;input_file_id\&quot;: \&quot;file-abc123\&quot;,         \&quot;endpoint\&quot;: \&quot;/v1/chat/completions\&quot;,         \&quot;completion_window\&quot;: \&quot;24h\&quot; }&#39; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **provider** | **String**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="createBatchProviderV1BatchesPost"></a>
# **createBatchProviderV1BatchesPost**
> oas_any_type_not_mapped createBatchProviderV1BatchesPost(provider)

Create Batch

    Create large batches of API requests for asynchronous processing. This is the equivalent of POST https://api.openai.com/v1/batch Supports Identical Params as: https://platform.openai.com/docs/api-reference/batch  Example Curl &#x60;&#x60;&#x60; curl http://localhost:4000/v1/batches         -H \&quot;Authorization: Bearer sk-1234\&quot;         -H \&quot;Content-Type: application/json\&quot;         -d &#39;{         \&quot;input_file_id\&quot;: \&quot;file-abc123\&quot;,         \&quot;endpoint\&quot;: \&quot;/v1/chat/completions\&quot;,         \&quot;completion_window\&quot;: \&quot;24h\&quot; }&#39; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **provider** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="createBatchV1BatchesPost"></a>
# **createBatchV1BatchesPost**
> oas_any_type_not_mapped createBatchV1BatchesPost(provider)

Create Batch

    Create large batches of API requests for asynchronous processing. This is the equivalent of POST https://api.openai.com/v1/batch Supports Identical Params as: https://platform.openai.com/docs/api-reference/batch  Example Curl &#x60;&#x60;&#x60; curl http://localhost:4000/v1/batches         -H \&quot;Authorization: Bearer sk-1234\&quot;         -H \&quot;Content-Type: application/json\&quot;         -d &#39;{         \&quot;input_file_id\&quot;: \&quot;file-abc123\&quot;,         \&quot;endpoint\&quot;: \&quot;/v1/chat/completions\&quot;,         \&quot;completion_window\&quot;: \&quot;24h\&quot; }&#39; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **provider** | **String**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="listBatchesBatchesGet"></a>
# **listBatchesBatchesGet**
> oas_any_type_not_mapped listBatchesBatchesGet(provider, limit, after)

List Batches

    Lists  This is the equivalent of GET https://api.openai.com/v1/batches/ Supports Identical Params as: https://platform.openai.com/docs/api-reference/batch/list  Example Curl &#x60;&#x60;&#x60; curl http://localhost:4000/v1/batches?limit&#x3D;2     -H \&quot;Authorization: Bearer sk-1234\&quot;     -H \&quot;Content-Type: application/json\&quot;  &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **provider** | **String**|  | [optional] [default to null] |
| **limit** | **Integer**|  | [optional] [default to null] |
| **after** | **String**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="listBatchesProviderV1BatchesGet"></a>
# **listBatchesProviderV1BatchesGet**
> oas_any_type_not_mapped listBatchesProviderV1BatchesGet(provider, limit, after)

List Batches

    Lists  This is the equivalent of GET https://api.openai.com/v1/batches/ Supports Identical Params as: https://platform.openai.com/docs/api-reference/batch/list  Example Curl &#x60;&#x60;&#x60; curl http://localhost:4000/v1/batches?limit&#x3D;2     -H \&quot;Authorization: Bearer sk-1234\&quot;     -H \&quot;Content-Type: application/json\&quot;  &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **provider** | **String**|  | [default to null] |
| **limit** | **Integer**|  | [optional] [default to null] |
| **after** | **String**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="listBatchesV1BatchesGet"></a>
# **listBatchesV1BatchesGet**
> oas_any_type_not_mapped listBatchesV1BatchesGet(provider, limit, after)

List Batches

    Lists  This is the equivalent of GET https://api.openai.com/v1/batches/ Supports Identical Params as: https://platform.openai.com/docs/api-reference/batch/list  Example Curl &#x60;&#x60;&#x60; curl http://localhost:4000/v1/batches?limit&#x3D;2     -H \&quot;Authorization: Bearer sk-1234\&quot;     -H \&quot;Content-Type: application/json\&quot;  &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **provider** | **String**|  | [optional] [default to null] |
| **limit** | **Integer**|  | [optional] [default to null] |
| **after** | **String**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="retrieveBatchBatchesBatchIdGet"></a>
# **retrieveBatchBatchesBatchIdGet**
> oas_any_type_not_mapped retrieveBatchBatchesBatchIdGet(batch\_id, provider)

Retrieve Batch

    Retrieves a batch. This is the equivalent of GET https://api.openai.com/v1/batches/{batch_id} Supports Identical Params as: https://platform.openai.com/docs/api-reference/batch/retrieve  Example Curl &#x60;&#x60;&#x60; curl http://localhost:4000/v1/batches/batch_abc123     -H \&quot;Authorization: Bearer sk-1234\&quot;     -H \&quot;Content-Type: application/json\&quot;  &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **batch\_id** | **String**| The ID of the batch to retrieve | [default to null] |
| **provider** | **String**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="retrieveBatchProviderV1BatchesBatchIdGet"></a>
# **retrieveBatchProviderV1BatchesBatchIdGet**
> oas_any_type_not_mapped retrieveBatchProviderV1BatchesBatchIdGet(provider, batch\_id)

Retrieve Batch

    Retrieves a batch. This is the equivalent of GET https://api.openai.com/v1/batches/{batch_id} Supports Identical Params as: https://platform.openai.com/docs/api-reference/batch/retrieve  Example Curl &#x60;&#x60;&#x60; curl http://localhost:4000/v1/batches/batch_abc123     -H \&quot;Authorization: Bearer sk-1234\&quot;     -H \&quot;Content-Type: application/json\&quot;  &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **provider** | **String**|  | [default to null] |
| **batch\_id** | **String**| The ID of the batch to retrieve | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="retrieveBatchV1BatchesBatchIdGet"></a>
# **retrieveBatchV1BatchesBatchIdGet**
> oas_any_type_not_mapped retrieveBatchV1BatchesBatchIdGet(batch\_id, provider)

Retrieve Batch

    Retrieves a batch. This is the equivalent of GET https://api.openai.com/v1/batches/{batch_id} Supports Identical Params as: https://platform.openai.com/docs/api-reference/batch/retrieve  Example Curl &#x60;&#x60;&#x60; curl http://localhost:4000/v1/batches/batch_abc123     -H \&quot;Authorization: Bearer sk-1234\&quot;     -H \&quot;Content-Type: application/json\&quot;  &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **batch\_id** | **String**| The ID of the batch to retrieve | [default to null] |
| **provider** | **String**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

