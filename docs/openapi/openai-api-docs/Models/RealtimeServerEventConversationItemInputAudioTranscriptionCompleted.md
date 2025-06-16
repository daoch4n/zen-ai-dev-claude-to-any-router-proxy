# RealtimeServerEventConversationItemInputAudioTranscriptionCompleted
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **event\_id** | **String** | The unique ID of the server event. | [default to null] |
| **type** | **String** | The event type, must be &#x60;conversation.item.input_audio_transcription.completed&#x60;.  | [default to null] |
| **item\_id** | **String** | The ID of the user message item containing the audio. | [default to null] |
| **content\_index** | **Integer** | The index of the content part containing the audio. | [default to null] |
| **transcript** | **String** | The transcribed text. | [default to null] |
| **logprobs** | [**List**](LogProbProperties.md) | The log probabilities of the transcription. | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

