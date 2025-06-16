# RealtimeSession_input_audio_transcription
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **model** | **String** | The model to use for transcription, current options are &#x60;gpt-4o-transcribe&#x60;, &#x60;gpt-4o-mini-transcribe&#x60;, and &#x60;whisper-1&#x60;.  | [optional] [default to null] |
| **language** | **String** | The language of the input audio. Supplying the input language in [ISO-639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) (e.g. &#x60;en&#x60;) format will improve accuracy and latency.  | [optional] [default to null] |
| **prompt** | **String** | An optional text to guide the model&#39;s style or continue a previous audio segment. For &#x60;whisper-1&#x60;, the [prompt is a list of keywords](/docs/guides/speech-to-text#prompting). For &#x60;gpt-4o-transcribe&#x60; models, the prompt is a free text string, for example \&quot;expect words related to technology\&quot;.  | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

