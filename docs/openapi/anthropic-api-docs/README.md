# Documentation for Anthropic API

<a name="documentation-for-api-endpoints"></a>
## Documentation for API Endpoints

All URIs are relative to *https://api.anthropic.com*

| Class | Method | HTTP request | Description |
|------------ | ------------- | ------------- | -------------|
| *MessageBatchesApi* | [**betaMessageBatchesCancel**](Apis/MessageBatchesApi.md#betamessagebatchescancel) | **POST** /v1/messages/batches/{message_batch_id}/cancel?beta&#x3D;true | Cancel a Message Batch |
*MessageBatchesApi* | [**betaMessageBatchesCancel_0**](Apis/MessageBatchesApi.md#betamessagebatchescancel_0) | **POST** /v1/messages/batches/{message_batch_id}/cancel | Cancel a Message Batch |
*MessageBatchesApi* | [**betaMessageBatchesList**](Apis/MessageBatchesApi.md#betamessagebatcheslist) | **GET** /v1/messages/batches?beta&#x3D;true | List Message Batches |
*MessageBatchesApi* | [**betaMessageBatchesList_0**](Apis/MessageBatchesApi.md#betamessagebatcheslist_0) | **GET** /v1/messages/batches | List Message Batches |
*MessageBatchesApi* | [**betaMessageBatchesPost**](Apis/MessageBatchesApi.md#betamessagebatchespost) | **POST** /v1/messages/batches?beta&#x3D;true | Create a Message Batch |
*MessageBatchesApi* | [**betaMessageBatchesPost_0**](Apis/MessageBatchesApi.md#betamessagebatchespost_0) | **POST** /v1/messages/batches | Create a Message Batch |
*MessageBatchesApi* | [**betaMessageBatchesResults**](Apis/MessageBatchesApi.md#betamessagebatchesresults) | **GET** /v1/messages/batches/{message_batch_id}/results?beta&#x3D;true | Retrieve Message Batch results |
*MessageBatchesApi* | [**betaMessageBatchesResults_0**](Apis/MessageBatchesApi.md#betamessagebatchesresults_0) | **GET** /v1/messages/batches/{message_batch_id}/results | Retrieve Message Batch results |
*MessageBatchesApi* | [**betaMessageBatchesRetrieve**](Apis/MessageBatchesApi.md#betamessagebatchesretrieve) | **GET** /v1/messages/batches/{message_batch_id}?beta&#x3D;true | Retrieve a Message Batch |
*MessageBatchesApi* | [**betaMessageBatchesRetrieve_0**](Apis/MessageBatchesApi.md#betamessagebatchesretrieve_0) | **GET** /v1/messages/batches/{message_batch_id} | Retrieve a Message Batch |
| *MessagesApi* | [**betaMessagesCountTokensPost**](Apis/MessagesApi.md#betamessagescounttokenspost) | **POST** /v1/messages/count_tokens?beta&#x3D;true | Count tokens in a Message |
*MessagesApi* | [**betaMessagesCountTokensPost_0**](Apis/MessagesApi.md#betamessagescounttokenspost_0) | **POST** /v1/messages/count_tokens | Count tokens in a Message |
*MessagesApi* | [**betaMessagesPost**](Apis/MessagesApi.md#betamessagespost) | **POST** /v1/messages?beta&#x3D;true | Create a Message |
*MessagesApi* | [**messagesPost**](Apis/MessagesApi.md#messagespost) | **POST** /v1/messages | Create a Message |
*MessagesApi* | [**promptCachingBetaMessagesPost**](Apis/MessagesApi.md#promptcachingbetamessagespost) | **POST** /v1/messages?beta&#x3D;prompt_caching | Create a Message |
| *TextCompletionsApi* | [**completePost**](Apis/TextCompletionsApi.md#completepost) | **POST** /v1/complete | Create a Text Completion |


<a name="documentation-for-models"></a>
## Documentation for Models

 - [APIError](./Models/APIError.md)
 - [AnthropicBeta](./Models/AnthropicBeta.md)
 - [AuthenticationError](./Models/AuthenticationError.md)
 - [Base64ImageSource](./Models/Base64ImageSource.md)
 - [BetaAPIError](./Models/BetaAPIError.md)
 - [BetaAuthenticationError](./Models/BetaAuthenticationError.md)
 - [BetaBase64ImageSource](./Models/BetaBase64ImageSource.md)
 - [BetaBase64PDFSource](./Models/BetaBase64PDFSource.md)
 - [BetaBashTool_20241022](./Models/BetaBashTool_20241022.md)
 - [BetaCacheControlEphemeral](./Models/BetaCacheControlEphemeral.md)
 - [BetaCanceledResult](./Models/BetaCanceledResult.md)
 - [BetaComputerUseTool_20241022](./Models/BetaComputerUseTool_20241022.md)
 - [BetaContentBlock](./Models/BetaContentBlock.md)
 - [BetaContentBlockDeltaEvent](./Models/BetaContentBlockDeltaEvent.md)
 - [BetaContentBlockStartEvent](./Models/BetaContentBlockStartEvent.md)
 - [BetaContentBlockStopEvent](./Models/BetaContentBlockStopEvent.md)
 - [BetaCountMessageTokensParams](./Models/BetaCountMessageTokensParams.md)
 - [BetaCountMessageTokensParams_tools_inner](./Models/BetaCountMessageTokensParams_tools_inner.md)
 - [BetaCountMessageTokensResponse](./Models/BetaCountMessageTokensResponse.md)
 - [BetaCreateMessageBatchParams](./Models/BetaCreateMessageBatchParams.md)
 - [BetaCreateMessageParams](./Models/BetaCreateMessageParams.md)
 - [BetaErrorResponse](./Models/BetaErrorResponse.md)
 - [BetaErroredResult](./Models/BetaErroredResult.md)
 - [BetaExpiredResult](./Models/BetaExpiredResult.md)
 - [BetaInputContentBlock](./Models/BetaInputContentBlock.md)
 - [BetaInputJsonContentBlockDelta](./Models/BetaInputJsonContentBlockDelta.md)
 - [BetaInputMessage](./Models/BetaInputMessage.md)
 - [BetaInputSchema](./Models/BetaInputSchema.md)
 - [BetaInvalidRequestError](./Models/BetaInvalidRequestError.md)
 - [BetaListResponse_MessageBatch_](./Models/BetaListResponse_MessageBatch_.md)
 - [BetaMessage](./Models/BetaMessage.md)
 - [BetaMessageBatch](./Models/BetaMessageBatch.md)
 - [BetaMessageBatchIndividualRequestParams](./Models/BetaMessageBatchIndividualRequestParams.md)
 - [BetaMessageBatchIndividualResponse](./Models/BetaMessageBatchIndividualResponse.md)
 - [BetaMessageBatchResult](./Models/BetaMessageBatchResult.md)
 - [BetaMessageDelta](./Models/BetaMessageDelta.md)
 - [BetaMessageDeltaEvent](./Models/BetaMessageDeltaEvent.md)
 - [BetaMessageDeltaUsage](./Models/BetaMessageDeltaUsage.md)
 - [BetaMessageStartEvent](./Models/BetaMessageStartEvent.md)
 - [BetaMessageStopEvent](./Models/BetaMessageStopEvent.md)
 - [BetaMessageStreamEvent](./Models/BetaMessageStreamEvent.md)
 - [BetaMetadata](./Models/BetaMetadata.md)
 - [BetaNotFoundError](./Models/BetaNotFoundError.md)
 - [BetaOverloadedError](./Models/BetaOverloadedError.md)
 - [BetaPermissionError](./Models/BetaPermissionError.md)
 - [BetaRateLimitError](./Models/BetaRateLimitError.md)
 - [BetaRequestCounts](./Models/BetaRequestCounts.md)
 - [BetaRequestImageBlock](./Models/BetaRequestImageBlock.md)
 - [BetaRequestPDFBlock](./Models/BetaRequestPDFBlock.md)
 - [BetaRequestTextBlock](./Models/BetaRequestTextBlock.md)
 - [BetaRequestToolResultBlock](./Models/BetaRequestToolResultBlock.md)
 - [BetaRequestToolUseBlock](./Models/BetaRequestToolUseBlock.md)
 - [BetaResponseTextBlock](./Models/BetaResponseTextBlock.md)
 - [BetaResponseToolUseBlock](./Models/BetaResponseToolUseBlock.md)
 - [BetaSucceededResult](./Models/BetaSucceededResult.md)
 - [BetaTextContentBlockDelta](./Models/BetaTextContentBlockDelta.md)
 - [BetaTextEditor_20241022](./Models/BetaTextEditor_20241022.md)
 - [BetaTool](./Models/BetaTool.md)
 - [BetaToolChoice](./Models/BetaToolChoice.md)
 - [BetaToolChoiceAny](./Models/BetaToolChoiceAny.md)
 - [BetaToolChoiceAuto](./Models/BetaToolChoiceAuto.md)
 - [BetaToolChoiceTool](./Models/BetaToolChoiceTool.md)
 - [BetaUsage](./Models/BetaUsage.md)
 - [Block](./Models/Block.md)
 - [Block_1](./Models/Block_1.md)
 - [Block_2](./Models/Block_2.md)
 - [Block_3](./Models/Block_3.md)
 - [Block_4](./Models/Block_4.md)
 - [CacheControlEphemeral](./Models/CacheControlEphemeral.md)
 - [CompletionRequest](./Models/CompletionRequest.md)
 - [CompletionResponse](./Models/CompletionResponse.md)
 - [Content](./Models/Content.md)
 - [ContentBlock](./Models/ContentBlock.md)
 - [ContentBlockDeltaEvent](./Models/ContentBlockDeltaEvent.md)
 - [ContentBlockStartEvent](./Models/ContentBlockStartEvent.md)
 - [ContentBlockStopEvent](./Models/ContentBlockStopEvent.md)
 - [Content_1](./Models/Content_1.md)
 - [Content_2](./Models/Content_2.md)
 - [Content_3](./Models/Content_3.md)
 - [Content_4](./Models/Content_4.md)
 - [Content_5](./Models/Content_5.md)
 - [Content_Block](./Models/Content_Block.md)
 - [Content_Block_1](./Models/Content_Block_1.md)
 - [CreateMessageParams](./Models/CreateMessageParams.md)
 - [CreateMessageParamsWithoutStream](./Models/CreateMessageParamsWithoutStream.md)
 - [Delta](./Models/Delta.md)
 - [Delta_1](./Models/Delta_1.md)
 - [Error](./Models/Error.md)
 - [ErrorResponse](./Models/ErrorResponse.md)
 - [Error_1](./Models/Error_1.md)
 - [InputJsonContentBlockDelta](./Models/InputJsonContentBlockDelta.md)
 - [InputMessage](./Models/InputMessage.md)
 - [InputSchema](./Models/InputSchema.md)
 - [InvalidRequestError](./Models/InvalidRequestError.md)
 - [Message](./Models/Message.md)
 - [MessageDelta](./Models/MessageDelta.md)
 - [MessageDeltaEvent](./Models/MessageDeltaEvent.md)
 - [MessageDeltaUsage](./Models/MessageDeltaUsage.md)
 - [MessageStartEvent](./Models/MessageStartEvent.md)
 - [MessageStopEvent](./Models/MessageStopEvent.md)
 - [MessageStreamEvent](./Models/MessageStreamEvent.md)
 - [Metadata](./Models/Metadata.md)
 - [Model](./Models/Model.md)
 - [NotFoundError](./Models/NotFoundError.md)
 - [OverloadedError](./Models/OverloadedError.md)
 - [PermissionError](./Models/PermissionError.md)
 - [PromptCachingBetaCreateMessageParams](./Models/PromptCachingBetaCreateMessageParams.md)
 - [PromptCachingBetaInputMessage](./Models/PromptCachingBetaInputMessage.md)
 - [PromptCachingBetaMessage](./Models/PromptCachingBetaMessage.md)
 - [PromptCachingBetaMessageStartEvent](./Models/PromptCachingBetaMessageStartEvent.md)
 - [PromptCachingBetaMessageStreamEvent](./Models/PromptCachingBetaMessageStreamEvent.md)
 - [PromptCachingBetaRequestImageBlock](./Models/PromptCachingBetaRequestImageBlock.md)
 - [PromptCachingBetaRequestTextBlock](./Models/PromptCachingBetaRequestTextBlock.md)
 - [PromptCachingBetaRequestToolResultBlock](./Models/PromptCachingBetaRequestToolResultBlock.md)
 - [PromptCachingBetaRequestToolUseBlock](./Models/PromptCachingBetaRequestToolUseBlock.md)
 - [PromptCachingBetaTool](./Models/PromptCachingBetaTool.md)
 - [PromptCachingBetaUsage](./Models/PromptCachingBetaUsage.md)
 - [RateLimitError](./Models/RateLimitError.md)
 - [RequestImageBlock](./Models/RequestImageBlock.md)
 - [RequestTextBlock](./Models/RequestTextBlock.md)
 - [RequestToolResultBlock](./Models/RequestToolResultBlock.md)
 - [RequestToolUseBlock](./Models/RequestToolUseBlock.md)
 - [ResponseTextBlock](./Models/ResponseTextBlock.md)
 - [ResponseToolUseBlock](./Models/ResponseToolUseBlock.md)
 - [System](./Models/System.md)
 - [System_1](./Models/System_1.md)
 - [System_2](./Models/System_2.md)
 - [System_3](./Models/System_3.md)
 - [System_4](./Models/System_4.md)
 - [TextContentBlockDelta](./Models/TextContentBlockDelta.md)
 - [Tool](./Models/Tool.md)
 - [ToolChoice](./Models/ToolChoice.md)
 - [ToolChoiceAny](./Models/ToolChoiceAny.md)
 - [ToolChoiceAuto](./Models/ToolChoiceAuto.md)
 - [ToolChoiceTool](./Models/ToolChoiceTool.md)
 - [Usage](./Models/Usage.md)


<a name="documentation-for-authorization"></a>
## Documentation for Authorization

All endpoints do not require authorization.
