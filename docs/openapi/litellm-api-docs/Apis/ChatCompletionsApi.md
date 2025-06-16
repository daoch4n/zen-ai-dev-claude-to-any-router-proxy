# ChatCompletionsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**chatCompletionChatCompletionsPost**](ChatCompletionsApi.md#chatCompletionChatCompletionsPost) | **POST** /chat/completions | Chat Completion |
| [**chatCompletionEnginesModelChatCompletionsPost**](ChatCompletionsApi.md#chatCompletionEnginesModelChatCompletionsPost) | **POST** /engines/{model}/chat/completions | Chat Completion |
| [**chatCompletionOpenaiDeploymentsModelChatCompletionsPost**](ChatCompletionsApi.md#chatCompletionOpenaiDeploymentsModelChatCompletionsPost) | **POST** /openai/deployments/{model}/chat/completions | Chat Completion |
| [**chatCompletionV1ChatCompletionsPost**](ChatCompletionsApi.md#chatCompletionV1ChatCompletionsPost) | **POST** /v1/chat/completions | Chat Completion |


<a name="chatCompletionChatCompletionsPost"></a>
# **chatCompletionChatCompletionsPost**
> oas_any_type_not_mapped chatCompletionChatCompletionsPost(model)

Chat Completion

    Follows the exact same API spec as &#x60;OpenAI&#39;s Chat API https://platform.openai.com/docs/api-reference/chat&#x60;  &#x60;&#x60;&#x60;bash curl -X POST http://localhost:4000/v1/chat/completions  -H \&quot;Content-Type: application/json\&quot;  -H \&quot;Authorization: Bearer sk-1234\&quot;  -d &#39;{     \&quot;model\&quot;: \&quot;gpt-4o\&quot;,     \&quot;messages\&quot;: [         {             \&quot;role\&quot;: \&quot;user\&quot;,             \&quot;content\&quot;: \&quot;Hello!\&quot;         }     ] }&#39; &#x60;&#x60;&#x60;

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

<a name="chatCompletionEnginesModelChatCompletionsPost"></a>
# **chatCompletionEnginesModelChatCompletionsPost**
> oas_any_type_not_mapped chatCompletionEnginesModelChatCompletionsPost(model)

Chat Completion

    Follows the exact same API spec as &#x60;OpenAI&#39;s Chat API https://platform.openai.com/docs/api-reference/chat&#x60;  &#x60;&#x60;&#x60;bash curl -X POST http://localhost:4000/v1/chat/completions  -H \&quot;Content-Type: application/json\&quot;  -H \&quot;Authorization: Bearer sk-1234\&quot;  -d &#39;{     \&quot;model\&quot;: \&quot;gpt-4o\&quot;,     \&quot;messages\&quot;: [         {             \&quot;role\&quot;: \&quot;user\&quot;,             \&quot;content\&quot;: \&quot;Hello!\&quot;         }     ] }&#39; &#x60;&#x60;&#x60;

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

<a name="chatCompletionOpenaiDeploymentsModelChatCompletionsPost"></a>
# **chatCompletionOpenaiDeploymentsModelChatCompletionsPost**
> oas_any_type_not_mapped chatCompletionOpenaiDeploymentsModelChatCompletionsPost(model)

Chat Completion

    Follows the exact same API spec as &#x60;OpenAI&#39;s Chat API https://platform.openai.com/docs/api-reference/chat&#x60;  &#x60;&#x60;&#x60;bash curl -X POST http://localhost:4000/v1/chat/completions  -H \&quot;Content-Type: application/json\&quot;  -H \&quot;Authorization: Bearer sk-1234\&quot;  -d &#39;{     \&quot;model\&quot;: \&quot;gpt-4o\&quot;,     \&quot;messages\&quot;: [         {             \&quot;role\&quot;: \&quot;user\&quot;,             \&quot;content\&quot;: \&quot;Hello!\&quot;         }     ] }&#39; &#x60;&#x60;&#x60;

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

<a name="chatCompletionV1ChatCompletionsPost"></a>
# **chatCompletionV1ChatCompletionsPost**
> oas_any_type_not_mapped chatCompletionV1ChatCompletionsPost(model)

Chat Completion

    Follows the exact same API spec as &#x60;OpenAI&#39;s Chat API https://platform.openai.com/docs/api-reference/chat&#x60;  &#x60;&#x60;&#x60;bash curl -X POST http://localhost:4000/v1/chat/completions  -H \&quot;Content-Type: application/json\&quot;  -H \&quot;Authorization: Bearer sk-1234\&quot;  -d &#39;{     \&quot;model\&quot;: \&quot;gpt-4o\&quot;,     \&quot;messages\&quot;: [         {             \&quot;role\&quot;: \&quot;user\&quot;,             \&quot;content\&quot;: \&quot;Hello!\&quot;         }     ] }&#39; &#x60;&#x60;&#x60;

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

