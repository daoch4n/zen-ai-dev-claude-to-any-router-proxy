# ResponsesApi

All URIs are relative to *https://api.openai.com/v1*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createResponse**](ResponsesApi.md#createResponse) | **POST** /responses | Creates a model response. Provide [text](/docs/guides/text) or [image](/docs/guides/images) inputs to generate [text](/docs/guides/text) or [JSON](/docs/guides/structured-outputs) outputs. Have the model call your own [custom code](/docs/guides/function-calling) or use built-in [tools](/docs/guides/tools) like [web search](/docs/guides/tools-web-search) or [file search](/docs/guides/tools-file-search) to use your own data as input for the model&#39;s response.  |
| [**deleteResponse**](ResponsesApi.md#deleteResponse) | **DELETE** /responses/{response_id} | Deletes a model response with the given ID.  |
| [**getResponse**](ResponsesApi.md#getResponse) | **GET** /responses/{response_id} | Retrieves a model response with the given ID.  |
| [**listInputItems**](ResponsesApi.md#listInputItems) | **GET** /responses/{response_id}/input_items | Returns a list of input items for a given response. |


<a name="createResponse"></a>
# **createResponse**
> Response createResponse(CreateResponse)

Creates a model response. Provide [text](/docs/guides/text) or [image](/docs/guides/images) inputs to generate [text](/docs/guides/text) or [JSON](/docs/guides/structured-outputs) outputs. Have the model call your own [custom code](/docs/guides/function-calling) or use built-in [tools](/docs/guides/tools) like [web search](/docs/guides/tools-web-search) or [file search](/docs/guides/tools-file-search) to use your own data as input for the model&#39;s response. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **CreateResponse** | [**CreateResponse**](../Models/CreateResponse.md)|  | |

### Return type

[**Response**](../Models/Response.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json, text/event-stream

<a name="deleteResponse"></a>
# **deleteResponse**
> deleteResponse(response\_id)

Deletes a model response with the given ID. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **response\_id** | **String**| The ID of the response to delete. | [default to null] |

### Return type

null (empty response body)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getResponse"></a>
# **getResponse**
> Response getResponse(response\_id, include)

Retrieves a model response with the given ID. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **response\_id** | **String**| The ID of the response to retrieve. | [default to null] |
| **include** | [**List**](../Models/Includable.md)| Additional fields to include in the response. See the &#x60;include&#x60; parameter for Response creation above for more information.  | [optional] [default to null] |

### Return type

[**Response**](../Models/Response.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="listInputItems"></a>
# **listInputItems**
> ResponseItemList listInputItems(response\_id, limit, order, after, before, include)

Returns a list of input items for a given response.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **response\_id** | **String**| The ID of the response to retrieve input items for. | [default to null] |
| **limit** | **Integer**| A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.  | [optional] [default to 20] |
| **order** | **String**| The order to return the input items in. Default is &#x60;asc&#x60;. - &#x60;asc&#x60;: Return the input items in ascending order. - &#x60;desc&#x60;: Return the input items in descending order.  | [optional] [default to null] [enum: asc, desc] |
| **after** | **String**| An item ID to list items after, used in pagination.  | [optional] [default to null] |
| **before** | **String**| An item ID to list items before, used in pagination.  | [optional] [default to null] |
| **include** | [**List**](../Models/Includable.md)| Additional fields to include in the response. See the &#x60;include&#x60; parameter for Response creation above for more information.  | [optional] [default to null] |

### Return type

[**ResponseItemList**](../Models/ResponseItemList.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

