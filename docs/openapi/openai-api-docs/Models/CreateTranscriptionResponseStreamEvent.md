# CreateTranscriptionResponseStreamEvent
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **type** | **String** | The type of the event. Always &#x60;transcript.text.delta&#x60;.  | [default to null] |
| **delta** | **String** | The text delta that was additionally transcribed.  | [default to null] |
| **logprobs** | [**List**](TranscriptTextDeltaEvent_logprobs_inner.md) | The log probabilities of the individual tokens in the transcription. Only included if you [create a transcription](/docs/api-reference/audio/create-transcription) with the &#x60;include[]&#x60; parameter set to &#x60;logprobs&#x60;.  | [optional] [default to null] |
| **text** | **String** | The text that was transcribed.  | [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

