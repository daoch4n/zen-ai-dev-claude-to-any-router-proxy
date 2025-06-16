# EmbeddingsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**embeddingsEmbeddingsPost**](EmbeddingsApi.md#embeddingsEmbeddingsPost) | **POST** /embeddings | Embeddings |
| [**embeddingsEnginesModelEmbeddingsPost**](EmbeddingsApi.md#embeddingsEnginesModelEmbeddingsPost) | **POST** /engines/{model}/embeddings | Embeddings |
| [**embeddingsOpenaiDeploymentsModelEmbeddingsPost**](EmbeddingsApi.md#embeddingsOpenaiDeploymentsModelEmbeddingsPost) | **POST** /openai/deployments/{model}/embeddings | Embeddings |
| [**embeddingsV1EmbeddingsPost**](EmbeddingsApi.md#embeddingsV1EmbeddingsPost) | **POST** /v1/embeddings | Embeddings |


<a name="embeddingsEmbeddingsPost"></a>
# **embeddingsEmbeddingsPost**
> oas_any_type_not_mapped embeddingsEmbeddingsPost(model)

Embeddings

    Follows the exact same API spec as &#x60;OpenAI&#39;s Embeddings API https://platform.openai.com/docs/api-reference/embeddings&#x60;  &#x60;&#x60;&#x60;bash curl -X POST http://localhost:4000/v1/embeddings  -H \&quot;Content-Type: application/json\&quot;  -H \&quot;Authorization: Bearer sk-1234\&quot;  -d &#39;{     \&quot;model\&quot;: \&quot;text-embedding-ada-002\&quot;,     \&quot;input\&quot;: \&quot;The quick brown fox jumps over the lazy dog\&quot; }&#39; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **model** | **String**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="embeddingsEnginesModelEmbeddingsPost"></a>
# **embeddingsEnginesModelEmbeddingsPost**
> oas_any_type_not_mapped embeddingsEnginesModelEmbeddingsPost(model)

Embeddings

    Follows the exact same API spec as &#x60;OpenAI&#39;s Embeddings API https://platform.openai.com/docs/api-reference/embeddings&#x60;  &#x60;&#x60;&#x60;bash curl -X POST http://localhost:4000/v1/embeddings  -H \&quot;Content-Type: application/json\&quot;  -H \&quot;Authorization: Bearer sk-1234\&quot;  -d &#39;{     \&quot;model\&quot;: \&quot;text-embedding-ada-002\&quot;,     \&quot;input\&quot;: \&quot;The quick brown fox jumps over the lazy dog\&quot; }&#39; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **model** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="embeddingsOpenaiDeploymentsModelEmbeddingsPost"></a>
# **embeddingsOpenaiDeploymentsModelEmbeddingsPost**
> oas_any_type_not_mapped embeddingsOpenaiDeploymentsModelEmbeddingsPost(model)

Embeddings

    Follows the exact same API spec as &#x60;OpenAI&#39;s Embeddings API https://platform.openai.com/docs/api-reference/embeddings&#x60;  &#x60;&#x60;&#x60;bash curl -X POST http://localhost:4000/v1/embeddings  -H \&quot;Content-Type: application/json\&quot;  -H \&quot;Authorization: Bearer sk-1234\&quot;  -d &#39;{     \&quot;model\&quot;: \&quot;text-embedding-ada-002\&quot;,     \&quot;input\&quot;: \&quot;The quick brown fox jumps over the lazy dog\&quot; }&#39; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **model** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="embeddingsV1EmbeddingsPost"></a>
# **embeddingsV1EmbeddingsPost**
> oas_any_type_not_mapped embeddingsV1EmbeddingsPost(model)

Embeddings

    Follows the exact same API spec as &#x60;OpenAI&#39;s Embeddings API https://platform.openai.com/docs/api-reference/embeddings&#x60;  &#x60;&#x60;&#x60;bash curl -X POST http://localhost:4000/v1/embeddings  -H \&quot;Content-Type: application/json\&quot;  -H \&quot;Authorization: Bearer sk-1234\&quot;  -d &#39;{     \&quot;model\&quot;: \&quot;text-embedding-ada-002\&quot;,     \&quot;input\&quot;: \&quot;The quick brown fox jumps over the lazy dog\&quot; }&#39; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **model** | **String**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

