# RealtimeSessionCreateResponse
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **client\_secret** | [**RealtimeSessionCreateResponse_client_secret**](RealtimeSessionCreateResponse_client_secret.md) |  | [default to null] |
| **modalities** | **List** | The set of modalities the model can respond with. To disable audio, set this to [\&quot;text\&quot;].  | [optional] [default to null] |
| **instructions** | **String** | The default system instructions (i.e. system message) prepended to model  calls. This field allows the client to guide the model on desired  responses. The model can be instructed on response content and format,  (e.g. \&quot;be extremely succinct\&quot;, \&quot;act friendly\&quot;, \&quot;here are examples of good  responses\&quot;) and on audio behavior (e.g. \&quot;talk quickly\&quot;, \&quot;inject emotion  into your voice\&quot;, \&quot;laugh frequently\&quot;). The instructions are not guaranteed  to be followed by the model, but they provide guidance to the model on the  desired behavior.  Note that the server sets default instructions which will be used if this  field is not set and are visible in the &#x60;session.created&#x60; event at the  start of the session.  | [optional] [default to null] |
| **voice** | [**VoiceIdsShared**](VoiceIdsShared.md) |  | [optional] [default to null] |
| **input\_audio\_format** | **String** | The format of input audio. Options are &#x60;pcm16&#x60;, &#x60;g711_ulaw&#x60;, or &#x60;g711_alaw&#x60;.  | [optional] [default to null] |
| **output\_audio\_format** | **String** | The format of output audio. Options are &#x60;pcm16&#x60;, &#x60;g711_ulaw&#x60;, or &#x60;g711_alaw&#x60;.  | [optional] [default to null] |
| **input\_audio\_transcription** | [**RealtimeSessionCreateResponse_input_audio_transcription**](RealtimeSessionCreateResponse_input_audio_transcription.md) |  | [optional] [default to null] |
| **turn\_detection** | [**RealtimeSessionCreateResponse_turn_detection**](RealtimeSessionCreateResponse_turn_detection.md) |  | [optional] [default to null] |
| **tools** | [**List**](RealtimeResponseCreateParams_tools_inner.md) | Tools (functions) available to the model. | [optional] [default to null] |
| **tool\_choice** | **String** | How the model chooses tools. Options are &#x60;auto&#x60;, &#x60;none&#x60;, &#x60;required&#x60;, or  specify a function.  | [optional] [default to null] |
| **temperature** | **BigDecimal** | Sampling temperature for the model, limited to [0.6, 1.2]. Defaults to 0.8.  | [optional] [default to null] |
| **max\_response\_output\_tokens** | [**RealtimeResponseCreateParams_max_response_output_tokens**](RealtimeResponseCreateParams_max_response_output_tokens.md) |  | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

