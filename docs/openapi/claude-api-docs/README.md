# Documentation for Claude Code CLI API

<a name="documentation-for-api-endpoints"></a>
## Documentation for API Endpoints

All URIs are relative to *https://api.anthropic.com*

| Class | Method | HTTP request | Description |
|------------ | ------------- | ------------- | -------------|
| *ClaudeAPIApi* | [**createMessage**](Apis/ClaudeAPIApi.md#createmessage) | **POST** /v1/messages | Create a message completion |
| *OAuthAPIApi* | [**authorize**](Apis/OAuthAPIApi.md#authorize) | **GET** /oauth2/auth | OAuth authorization endpoint |
*OAuthAPIApi* | [**token**](Apis/OAuthAPIApi.md#token) | **POST** /oauth2/token | OAuth token endpoint |
| *TelemetryAPIApi* | [**submitTelemetryEvents**](Apis/TelemetryAPIApi.md#submittelemetryevents) | **POST** /claude-code/events | Submit telemetry events |


<a name="documentation-for-models"></a>
## Documentation for Models

 - [ClientInfo](./Models/ClientInfo.md)
 - [ContentBlock](./Models/ContentBlock.md)
 - [ErrorResponse](./Models/ErrorResponse.md)
 - [ErrorResponse_error](./Models/ErrorResponse_error.md)
 - [Message](./Models/Message.md)
 - [MessageRequest](./Models/MessageRequest.md)
 - [MessageResponse](./Models/MessageResponse.md)
 - [OAuthErrorResponse](./Models/OAuthErrorResponse.md)
 - [TelemetryEvent](./Models/TelemetryEvent.md)
 - [TokenResponse](./Models/TokenResponse.md)
 - [Usage](./Models/Usage.md)


<a name="documentation-for-authorization"></a>
## Documentation for Authorization

<a name="ApiKeyAuth"></a>
### ApiKeyAuth

- **Type**: API key
- **API key parameter name**: X-Api-Key
- **Location**: HTTP header

