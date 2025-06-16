# CompletionsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**completionCompletionsPost**](CompletionsApi.md#completionCompletionsPost) | **POST** /completions | Completion |
| [**completionEnginesModelCompletionsPost**](CompletionsApi.md#completionEnginesModelCompletionsPost) | **POST** /engines/{model}/completions | Completion |
| [**completionOpenaiDeploymentsModelCompletionsPost**](CompletionsApi.md#completionOpenaiDeploymentsModelCompletionsPost) | **POST** /openai/deployments/{model}/completions | Completion |
| [**completionV1CompletionsPost**](CompletionsApi.md#completionV1CompletionsPost) | **POST** /v1/completions | Completion |


<a name="completionCompletionsPost"></a>
# **completionCompletionsPost**
> oas_any_type_not_mapped completionCompletionsPost(model)

Completion

    Follows the exact same API spec as &#x60;OpenAI&#39;s Completions API https://platform.openai.com/docs/api-reference/completions&#x60;  &#x60;&#x60;&#x60;bash curl -X POST http://localhost:4000/v1/completions  -H \&quot;Content-Type: application/json\&quot;  -H \&quot;Authorization: Bearer sk-1234\&quot;  -d &#39;{     \&quot;model\&quot;: \&quot;gpt-3.5-turbo-instruct\&quot;,     \&quot;prompt\&quot;: \&quot;Once upon a time\&quot;,     \&quot;max_tokens\&quot;: 50,     \&quot;temperature\&quot;: 0.7 }&#39; &#x60;&#x60;&#x60;

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

<a name="completionEnginesModelCompletionsPost"></a>
# **completionEnginesModelCompletionsPost**
> oas_any_type_not_mapped completionEnginesModelCompletionsPost(model)

Completion

    Follows the exact same API spec as &#x60;OpenAI&#39;s Completions API https://platform.openai.com/docs/api-reference/completions&#x60;  &#x60;&#x60;&#x60;bash curl -X POST http://localhost:4000/v1/completions  -H \&quot;Content-Type: application/json\&quot;  -H \&quot;Authorization: Bearer sk-1234\&quot;  -d &#39;{     \&quot;model\&quot;: \&quot;gpt-3.5-turbo-instruct\&quot;,     \&quot;prompt\&quot;: \&quot;Once upon a time\&quot;,     \&quot;max_tokens\&quot;: 50,     \&quot;temperature\&quot;: 0.7 }&#39; &#x60;&#x60;&#x60;

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

<a name="completionOpenaiDeploymentsModelCompletionsPost"></a>
# **completionOpenaiDeploymentsModelCompletionsPost**
> oas_any_type_not_mapped completionOpenaiDeploymentsModelCompletionsPost(model)

Completion

    Follows the exact same API spec as &#x60;OpenAI&#39;s Completions API https://platform.openai.com/docs/api-reference/completions&#x60;  &#x60;&#x60;&#x60;bash curl -X POST http://localhost:4000/v1/completions  -H \&quot;Content-Type: application/json\&quot;  -H \&quot;Authorization: Bearer sk-1234\&quot;  -d &#39;{     \&quot;model\&quot;: \&quot;gpt-3.5-turbo-instruct\&quot;,     \&quot;prompt\&quot;: \&quot;Once upon a time\&quot;,     \&quot;max_tokens\&quot;: 50,     \&quot;temperature\&quot;: 0.7 }&#39; &#x60;&#x60;&#x60;

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

<a name="completionV1CompletionsPost"></a>
# **completionV1CompletionsPost**
> oas_any_type_not_mapped completionV1CompletionsPost(model)

Completion

    Follows the exact same API spec as &#x60;OpenAI&#39;s Completions API https://platform.openai.com/docs/api-reference/completions&#x60;  &#x60;&#x60;&#x60;bash curl -X POST http://localhost:4000/v1/completions  -H \&quot;Content-Type: application/json\&quot;  -H \&quot;Authorization: Bearer sk-1234\&quot;  -d &#39;{     \&quot;model\&quot;: \&quot;gpt-3.5-turbo-instruct\&quot;,     \&quot;prompt\&quot;: \&quot;Once upon a time\&quot;,     \&quot;max_tokens\&quot;: 50,     \&quot;temperature\&quot;: 0.7 }&#39; &#x60;&#x60;&#x60;

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

