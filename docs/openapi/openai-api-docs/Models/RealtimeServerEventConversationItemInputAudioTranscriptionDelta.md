# RealtimeServerEventConversationItemInputAudioTranscriptionDelta
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **event\_id** | **String** | The unique ID of the server event. | [default to null] |
| **type** | **String** | The event type, must be &#x60;conversation.item.input_audio_transcription.delta&#x60;. | [default to null] |
| **item\_id** | **String** | The ID of the item. | [default to null] |
| **content\_index** | **Integer** | The index of the content part in the item&#39;s content array. | [optional] [default to null] |
| **delta** | **String** | The text delta. | [optional] [default to null] |
| **logprobs** | [**List**](LogProbProperties.md) | The log probabilities of the transcription. | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

