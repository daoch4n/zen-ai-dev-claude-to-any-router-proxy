# ResponsesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**deleteResponseResponsesResponseIdDelete**](ResponsesApi.md#deleteResponseResponsesResponseIdDelete) | **DELETE** /responses/{response_id} | Delete Response |
| [**deleteResponseV1ResponsesResponseIdDelete**](ResponsesApi.md#deleteResponseV1ResponsesResponseIdDelete) | **DELETE** /v1/responses/{response_id} | Delete Response |
| [**getResponseInputItemsResponsesResponseIdInputItemsGet**](ResponsesApi.md#getResponseInputItemsResponsesResponseIdInputItemsGet) | **GET** /responses/{response_id}/input_items | Get Response Input Items |
| [**getResponseInputItemsV1ResponsesResponseIdInputItemsGet**](ResponsesApi.md#getResponseInputItemsV1ResponsesResponseIdInputItemsGet) | **GET** /v1/responses/{response_id}/input_items | Get Response Input Items |
| [**getResponseResponsesResponseIdGet**](ResponsesApi.md#getResponseResponsesResponseIdGet) | **GET** /responses/{response_id} | Get Response |
| [**getResponseV1ResponsesResponseIdGet**](ResponsesApi.md#getResponseV1ResponsesResponseIdGet) | **GET** /v1/responses/{response_id} | Get Response |
| [**responsesApiResponsesPost**](ResponsesApi.md#responsesApiResponsesPost) | **POST** /responses | Responses Api |
| [**responsesApiV1ResponsesPost**](ResponsesApi.md#responsesApiV1ResponsesPost) | **POST** /v1/responses | Responses Api |


<a name="deleteResponseResponsesResponseIdDelete"></a>
# **deleteResponseResponsesResponseIdDelete**
> oas_any_type_not_mapped deleteResponseResponsesResponseIdDelete(response\_id)

Delete Response

    Delete a response by ID.  Follows the OpenAI Responses API spec: https://platform.openai.com/docs/api-reference/responses/delete  &#x60;&#x60;&#x60;bash curl -X DELETE http://localhost:4000/v1/responses/resp_abc123     -H \&quot;Authorization: Bearer sk-1234\&quot; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **response\_id** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="deleteResponseV1ResponsesResponseIdDelete"></a>
# **deleteResponseV1ResponsesResponseIdDelete**
> oas_any_type_not_mapped deleteResponseV1ResponsesResponseIdDelete(response\_id)

Delete Response

    Delete a response by ID.  Follows the OpenAI Responses API spec: https://platform.openai.com/docs/api-reference/responses/delete  &#x60;&#x60;&#x60;bash curl -X DELETE http://localhost:4000/v1/responses/resp_abc123     -H \&quot;Authorization: Bearer sk-1234\&quot; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **response\_id** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getResponseInputItemsResponsesResponseIdInputItemsGet"></a>
# **getResponseInputItemsResponsesResponseIdInputItemsGet**
> oas_any_type_not_mapped getResponseInputItemsResponsesResponseIdInputItemsGet(response\_id)

Get Response Input Items

    Get input items for a response.  Follows the OpenAI Responses API spec: https://platform.openai.com/docs/api-reference/responses/input-items  &#x60;&#x60;&#x60;bash curl -X GET http://localhost:4000/v1/responses/resp_abc123/input_items     -H \&quot;Authorization: Bearer sk-1234\&quot; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **response\_id** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getResponseInputItemsV1ResponsesResponseIdInputItemsGet"></a>
# **getResponseInputItemsV1ResponsesResponseIdInputItemsGet**
> oas_any_type_not_mapped getResponseInputItemsV1ResponsesResponseIdInputItemsGet(response\_id)

Get Response Input Items

    Get input items for a response.  Follows the OpenAI Responses API spec: https://platform.openai.com/docs/api-reference/responses/input-items  &#x60;&#x60;&#x60;bash curl -X GET http://localhost:4000/v1/responses/resp_abc123/input_items     -H \&quot;Authorization: Bearer sk-1234\&quot; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **response\_id** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getResponseResponsesResponseIdGet"></a>
# **getResponseResponsesResponseIdGet**
> oas_any_type_not_mapped getResponseResponsesResponseIdGet(response\_id)

Get Response

    Get a response by ID.  Follows the OpenAI Responses API spec: https://platform.openai.com/docs/api-reference/responses/get  &#x60;&#x60;&#x60;bash curl -X GET http://localhost:4000/v1/responses/resp_abc123     -H \&quot;Authorization: Bearer sk-1234\&quot; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **response\_id** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getResponseV1ResponsesResponseIdGet"></a>
# **getResponseV1ResponsesResponseIdGet**
> oas_any_type_not_mapped getResponseV1ResponsesResponseIdGet(response\_id)

Get Response

    Get a response by ID.  Follows the OpenAI Responses API spec: https://platform.openai.com/docs/api-reference/responses/get  &#x60;&#x60;&#x60;bash curl -X GET http://localhost:4000/v1/responses/resp_abc123     -H \&quot;Authorization: Bearer sk-1234\&quot; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **response\_id** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="responsesApiResponsesPost"></a>
# **responsesApiResponsesPost**
> oas_any_type_not_mapped responsesApiResponsesPost()

Responses Api

    Follows the OpenAI Responses API spec: https://platform.openai.com/docs/api-reference/responses  &#x60;&#x60;&#x60;bash curl -X POST http://localhost:4000/v1/responses     -H \&quot;Content-Type: application/json\&quot;     -H \&quot;Authorization: Bearer sk-1234\&quot;     -d &#39;{     \&quot;model\&quot;: \&quot;gpt-4o\&quot;,     \&quot;input\&quot;: \&quot;Tell me about AI\&quot; }&#39; &#x60;&#x60;&#x60;

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="responsesApiV1ResponsesPost"></a>
# **responsesApiV1ResponsesPost**
> oas_any_type_not_mapped responsesApiV1ResponsesPost()

Responses Api

    Follows the OpenAI Responses API spec: https://platform.openai.com/docs/api-reference/responses  &#x60;&#x60;&#x60;bash curl -X POST http://localhost:4000/v1/responses     -H \&quot;Content-Type: application/json\&quot;     -H \&quot;Authorization: Bearer sk-1234\&quot;     -d &#39;{     \&quot;model\&quot;: \&quot;gpt-4o\&quot;,     \&quot;input\&quot;: \&quot;Tell me about AI\&quot; }&#39; &#x60;&#x60;&#x60;

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

