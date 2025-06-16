# MessagesApi

All URIs are relative to *https://api.anthropic.com*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**betaMessagesCountTokensPost**](MessagesApi.md#betaMessagesCountTokensPost) | **POST** /v1/messages/count_tokens?beta&#x3D;true | Count tokens in a Message |
| [**betaMessagesCountTokensPost_0**](MessagesApi.md#betaMessagesCountTokensPost_0) | **POST** /v1/messages/count_tokens | Count tokens in a Message |
| [**betaMessagesPost**](MessagesApi.md#betaMessagesPost) | **POST** /v1/messages?beta&#x3D;true | Create a Message |
| [**messagesPost**](MessagesApi.md#messagesPost) | **POST** /v1/messages | Create a Message |
| [**promptCachingBetaMessagesPost**](MessagesApi.md#promptCachingBetaMessagesPost) | **POST** /v1/messages?beta&#x3D;prompt_caching | Create a Message |


<a name="betaMessagesCountTokensPost"></a>
# **betaMessagesCountTokensPost**
> BetaCountMessageTokensResponse betaMessagesCountTokensPost(BetaCountMessageTokensParams, anthropic-beta, anthropic-version)

Count tokens in a Message

    Count the number of tokens in a Message.  The Token Count API can be used to count the number of tokens in a Message, including tools, images, and documents, without creating it.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **BetaCountMessageTokensParams** | [**BetaCountMessageTokensParams**](../Models/BetaCountMessageTokensParams.md)|  | |
| **anthropic-beta** | **String**| Optional header to specify the beta version(s) you want to use.  To use multiple betas, use a comma separated list like &#x60;beta1,beta2&#x60; or specify the header multiple times for each beta. | [optional] [default to null] |
| **anthropic-version** | **String**| The version of the Anthropic API you want to use.  Read more about versioning and our version history [here](https://docs.anthropic.com/en/api/versioning). | [optional] [default to null] |

### Return type

[**BetaCountMessageTokensResponse**](../Models/BetaCountMessageTokensResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="betaMessagesCountTokensPost_0"></a>
# **betaMessagesCountTokensPost_0**
> BetaCountMessageTokensResponse betaMessagesCountTokensPost_0(BetaCountMessageTokensParams, anthropic-beta, anthropic-version)

Count tokens in a Message

    Count the number of tokens in a Message.  The Token Count API can be used to count the number of tokens in a Message, including tools, images, and documents, without creating it.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **BetaCountMessageTokensParams** | [**BetaCountMessageTokensParams**](../Models/BetaCountMessageTokensParams.md)|  | |
| **anthropic-beta** | **String**| Optional header to specify the beta version(s) you want to use.  To use multiple betas, use a comma separated list like &#x60;beta1,beta2&#x60; or specify the header multiple times for each beta. | [optional] [default to null] |
| **anthropic-version** | **String**| The version of the Anthropic API you want to use.  Read more about versioning and our version history [here](https://docs.anthropic.com/en/api/versioning). | [optional] [default to null] |

### Return type

[**BetaCountMessageTokensResponse**](../Models/BetaCountMessageTokensResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="betaMessagesPost"></a>
# **betaMessagesPost**
> BetaMessage betaMessagesPost(BetaCreateMessageParams, anthropic-beta, anthropic-version)

Create a Message

    Send a structured list of input messages with text and/or image content, and the model will generate the next message in the conversation.  The Messages API can be used for either single queries or stateless multi-turn conversations.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **BetaCreateMessageParams** | [**BetaCreateMessageParams**](../Models/BetaCreateMessageParams.md)|  | |
| **anthropic-beta** | **String**| Optional header to specify the beta version(s) you want to use.  To use multiple betas, use a comma separated list like &#x60;beta1,beta2&#x60; or specify the header multiple times for each beta. | [optional] [default to null] |
| **anthropic-version** | **String**| The version of the Anthropic API you want to use.  Read more about versioning and our version history [here](https://docs.anthropic.com/en/api/versioning). | [optional] [default to null] |

### Return type

[**BetaMessage**](../Models/BetaMessage.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="messagesPost"></a>
# **messagesPost**
> Message messagesPost(CreateMessageParams, anthropic-version)

Create a Message

    Send a structured list of input messages with text and/or image content, and the model will generate the next message in the conversation.  The Messages API can be used for either single queries or stateless multi-turn conversations.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **CreateMessageParams** | [**CreateMessageParams**](../Models/CreateMessageParams.md)|  | |
| **anthropic-version** | **String**| The version of the Anthropic API you want to use.  Read more about versioning and our version history [here](https://docs.anthropic.com/en/api/versioning). | [optional] [default to null] |

### Return type

[**Message**](../Models/Message.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="promptCachingBetaMessagesPost"></a>
# **promptCachingBetaMessagesPost**
> PromptCachingBetaMessage promptCachingBetaMessagesPost(PromptCachingBetaCreateMessageParams, anthropic-beta, anthropic-version)

Create a Message

    Send a structured list of input messages with text and/or image content, and the model will generate the next message in the conversation.  The Messages API can be used for either single queries or stateless multi-turn conversations.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **PromptCachingBetaCreateMessageParams** | [**PromptCachingBetaCreateMessageParams**](../Models/PromptCachingBetaCreateMessageParams.md)|  | |
| **anthropic-beta** | **String**| Optional header to specify the beta version(s) you want to use.  To use multiple betas, use a comma separated list like &#x60;beta1,beta2&#x60; or specify the header multiple times for each beta. | [optional] [default to null] |
| **anthropic-version** | **String**| The version of the Anthropic API you want to use.  Read more about versioning and our version history [here](https://docs.anthropic.com/en/api/versioning). | [optional] [default to null] |

### Return type

[**PromptCachingBetaMessage**](../Models/PromptCachingBetaMessage.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

