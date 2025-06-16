# CreateTranscriptionResponseJson
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **text** | **String** | The transcribed text. | [default to null] |
| **logprobs** | [**List**](CreateTranscriptionResponseJson_logprobs_inner.md) | The log probabilities of the tokens in the transcription. Only returned with the models &#x60;gpt-4o-transcribe&#x60; and &#x60;gpt-4o-mini-transcribe&#x60; if &#x60;logprobs&#x60; is added to the &#x60;include&#x60; array.  | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

