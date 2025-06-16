# RealtimeTranscriptionSessionCreateRequest
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **modalities** | **List** | The set of modalities the model can respond with. To disable audio, set this to [\&quot;text\&quot;].  | [optional] [default to null] |
| **input\_audio\_format** | **String** | The format of input audio. Options are &#x60;pcm16&#x60;, &#x60;g711_ulaw&#x60;, or &#x60;g711_alaw&#x60;. For &#x60;pcm16&#x60;, input audio must be 16-bit PCM at a 24kHz sample rate,  single channel (mono), and little-endian byte order.  | [optional] [default to pcm16] |
| **input\_audio\_transcription** | [**RealtimeTranscriptionSessionCreateRequest_input_audio_transcription**](RealtimeTranscriptionSessionCreateRequest_input_audio_transcription.md) |  | [optional] [default to null] |
| **turn\_detection** | [**RealtimeTranscriptionSessionCreateRequest_turn_detection**](RealtimeTranscriptionSessionCreateRequest_turn_detection.md) |  | [optional] [default to null] |
| **input\_audio\_noise\_reduction** | [**RealtimeSession_input_audio_noise_reduction**](RealtimeSession_input_audio_noise_reduction.md) |  | [optional] [default to null] |
| **include** | **List** | The set of items to include in the transcription. Current available items are: - &#x60;item.input_audio_transcription.logprobs&#x60;  | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

