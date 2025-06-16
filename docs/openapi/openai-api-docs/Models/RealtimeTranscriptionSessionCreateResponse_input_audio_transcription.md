# RealtimeTranscriptionSessionCreateResponse_input_audio_transcription
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **model** | **String** | The model to use for transcription. Can be &#x60;gpt-4o-transcribe&#x60;, &#x60;gpt-4o-mini-transcribe&#x60;, or &#x60;whisper-1&#x60;.  | [optional] [default to null] |
| **language** | **String** | The language of the input audio. Supplying the input language in [ISO-639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) (e.g. &#x60;en&#x60;) format will improve accuracy and latency.  | [optional] [default to null] |
| **prompt** | **String** | An optional text to guide the model&#39;s style or continue a previous audio segment. The [prompt](/docs/guides/speech-to-text#prompting) should match the audio language.  | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

