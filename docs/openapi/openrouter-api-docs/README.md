# Documentation for OpenRouter API

<a name="documentation-for-api-endpoints"></a>
## Documentation for API Endpoints

All URIs are relative to *https://openrouter.ai/api/v1*

| Class | Method | HTTP request | Description |
|------------ | ------------- | ------------- | -------------|
| *AuthenticationApi* | [**getKeyInfo**](Apis/AuthenticationApi.md#getkeyinfo) | **GET** /auth/key | Get API key information |
| *ChatApi* | [**createChatCompletion**](Apis/ChatApi.md#createchatcompletion) | **POST** /chat/completions | Create chat completion |
| *CreditsApi* | [**getCredits**](Apis/CreditsApi.md#getcredits) | **GET** /credits | Get credit balance |
| *GenerationsApi* | [**getGeneration**](Apis/GenerationsApi.md#getgeneration) | **GET** /generation | Get generation details |
| *ModelsApi* | [**listModels**](Apis/ModelsApi.md#listmodels) | **GET** /models | List available models |


<a name="documentation-for-models"></a>
## Documentation for Models

 - [ChatChoice](./Models/ChatChoice.md)
 - [ChatCompletionRequest](./Models/ChatCompletionRequest.md)
 - [ChatCompletionRequest_response_format](./Models/ChatCompletionRequest_response_format.md)
 - [ChatCompletionRequest_stop](./Models/ChatCompletionRequest_stop.md)
 - [ChatCompletionResponse](./Models/ChatCompletionResponse.md)
 - [ChatMessage](./Models/ChatMessage.md)
 - [ChatMessage_content](./Models/ChatMessage_content.md)
 - [ContentPart](./Models/ContentPart.md)
 - [Credits](./Models/Credits.md)
 - [Credits_data](./Models/Credits_data.md)
 - [Error](./Models/Error.md)
 - [Error_error](./Models/Error_error.md)
 - [FunctionDefinition](./Models/FunctionDefinition.md)
 - [Generation](./Models/Generation.md)
 - [ImageContent](./Models/ImageContent.md)
 - [ImageContent_image_url](./Models/ImageContent_image_url.md)
 - [KeyInfo](./Models/KeyInfo.md)
 - [KeyInfo_data](./Models/KeyInfo_data.md)
 - [KeyInfo_data_rate_limit](./Models/KeyInfo_data_rate_limit.md)
 - [Model](./Models/Model.md)
 - [ModelList](./Models/ModelList.md)
 - [Model_pricing](./Models/Model_pricing.md)
 - [ProviderPreferences](./Models/ProviderPreferences.md)
 - [TextContent](./Models/TextContent.md)
 - [Tool](./Models/Tool.md)
 - [ToolChoice](./Models/ToolChoice.md)
 - [ToolChoice_oneOf](./Models/ToolChoice_oneOf.md)
 - [ToolChoice_oneOf_function](./Models/ToolChoice_oneOf_function.md)
 - [Usage](./Models/Usage.md)


<a name="documentation-for-authorization"></a>
## Documentation for Authorization

<a name="BearerAuth"></a>
### BearerAuth

- **Type**: HTTP Bearer Token authentication

