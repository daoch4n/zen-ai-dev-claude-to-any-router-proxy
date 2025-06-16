# ClaudeAPIApi

All URIs are relative to *https://api.anthropic.com*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createMessage**](ClaudeAPIApi.md#createMessage) | **POST** /v1/messages | Create a message completion |


<a name="createMessage"></a>
# **createMessage**
> MessageResponse createMessage(MessageRequest)

Create a message completion

    Generate a completion for a conversation using Claude. Supports both streaming and non-streaming responses. This is the primary endpoint used by Claude Code CLI for AI interactions. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **MessageRequest** | [**MessageRequest**](../Models/MessageRequest.md)|  | |

### Return type

[**MessageResponse**](../Models/MessageResponse.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json, text/event-stream

