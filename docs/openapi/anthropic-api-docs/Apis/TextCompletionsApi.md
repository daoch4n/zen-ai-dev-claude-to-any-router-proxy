# TextCompletionsApi

All URIs are relative to *https://api.anthropic.com*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**completePost**](TextCompletionsApi.md#completePost) | **POST** /v1/complete | Create a Text Completion |


<a name="completePost"></a>
# **completePost**
> CompletionResponse completePost(CompletionRequest, anthropic-version)

Create a Text Completion

    [Legacy] Create a Text Completion.  The Text Completions API is a legacy API. We recommend using the [Messages API](https://docs.anthropic.com/en/api/messages) going forward.  Future models and features will not be compatible with Text Completions. See our [migration guide](https://docs.anthropic.com/en/api/migrating-from-text-completions-to-messages) for guidance in migrating from Text Completions to Messages.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **CompletionRequest** | [**CompletionRequest**](../Models/CompletionRequest.md)|  | |
| **anthropic-version** | **String**| The version of the Anthropic API you want to use.  Read more about versioning and our version history [here](https://docs.anthropic.com/en/api/versioning). | [optional] [default to null] |

### Return type

[**CompletionResponse**](../Models/CompletionResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

