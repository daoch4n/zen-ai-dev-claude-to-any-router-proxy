# RealtimeServerEvent
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **event\_id** | **String** | The unique ID of the server event. | [default to null] |
| **type** | **String** | The event type, must be &#x60;conversation.created&#x60;. | [default to null] |
| **conversation** | [**RealtimeServerEventConversationCreated_conversation**](RealtimeServerEventConversationCreated_conversation.md) |  | [default to null] |
| **previous\_item\_id** | **String** | The ID of the preceding item after which the new item will be inserted.  | [default to null] |
| **item** | [**RealtimeConversationItem**](RealtimeConversationItem.md) |  | [default to null] |
| **item\_id** | **String** | The ID of the item. | [default to null] |
| **content\_index** | **Integer** | The index of the content part in the item&#39;s content array. | [default to null] |
| **transcript** | **String** | The final transcript of the audio. | [default to null] |
| **logprobs** | [**List**](LogProbProperties.md) | The log probabilities of the transcription. | [optional] [default to null] |
| **delta** | **String** | The text delta. | [default to null] |
| **error** | [**RealtimeServerEventError_error**](RealtimeServerEventError_error.md) |  | [default to null] |
| **audio\_end\_ms** | **Integer** | Milliseconds since the session started when speech stopped. This will  correspond to the end of audio sent to the model, and thus includes the  &#x60;min_silence_duration_ms&#x60; configured in the Session.  | [default to null] |
| **audio\_start\_ms** | **Integer** | Milliseconds from the start of all audio written to the buffer during the  session when speech was first detected. This will correspond to the  beginning of audio sent to the model, and thus includes the  &#x60;prefix_padding_ms&#x60; configured in the Session.  | [default to null] |
| **rate\_limits** | [**List**](RealtimeServerEventRateLimitsUpdated_rate_limits_inner.md) | List of rate limit information. | [default to null] |
| **response\_id** | **String** | The unique ID of the response that produced the audio. | [default to null] |
| **output\_index** | **Integer** | The index of the output item in the response. | [default to null] |
| **part** | [**RealtimeServerEventResponseContentPartDone_part**](RealtimeServerEventResponseContentPartDone_part.md) |  | [default to null] |
| **response** | [**RealtimeResponse**](RealtimeResponse.md) |  | [default to null] |
| **call\_id** | **String** | The ID of the function call. | [default to null] |
| **arguments** | **String** | The final arguments as a JSON string. | [default to null] |
| **text** | **String** | The final text content. | [default to null] |
| **session** | [**RealtimeTranscriptionSessionCreateResponse**](RealtimeTranscriptionSessionCreateResponse.md) |  | [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

