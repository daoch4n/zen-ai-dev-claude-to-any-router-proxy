# AudioApi

All URIs are relative to *https://api.openai.com/v1*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createSpeech**](AudioApi.md#createSpeech) | **POST** /audio/speech | Generates audio from the input text. |
| [**createTranscription**](AudioApi.md#createTranscription) | **POST** /audio/transcriptions | Transcribes audio into the input language. |
| [**createTranslation**](AudioApi.md#createTranslation) | **POST** /audio/translations | Translates audio into English. |


<a name="createSpeech"></a>
# **createSpeech**
> File createSpeech(CreateSpeechRequest)

Generates audio from the input text.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **CreateSpeechRequest** | [**CreateSpeechRequest**](../Models/CreateSpeechRequest.md)|  | |

### Return type

**File**

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/octet-stream

<a name="createTranscription"></a>
# **createTranscription**
> createTranscription_200_response createTranscription(file, model, language, prompt, response\_format, temperature, include\[\], timestamp\_granularities\[\], stream)

Transcribes audio into the input language.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **file** | **File**| The audio file object (not file name) to transcribe, in one of these formats: flac, mp3, mp4, mpeg, mpga, m4a, ogg, wav, or webm.  | [default to null] |
| **model** | [**CreateTranscriptionRequest_model**](../Models/CreateTranscriptionRequest_model.md)|  | [default to null] |
| **language** | **String**| The language of the input audio. Supplying the input language in [ISO-639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) (e.g. &#x60;en&#x60;) format will improve accuracy and latency.  | [optional] [default to null] |
| **prompt** | **String**| An optional text to guide the model&#39;s style or continue a previous audio segment. The [prompt](/docs/guides/speech-to-text#prompting) should match the audio language.  | [optional] [default to null] |
| **response\_format** | [**AudioResponseFormat**](../Models/AudioResponseFormat.md)|  | [optional] [default to null] [enum: json, text, srt, verbose_json, vtt] |
| **temperature** | **BigDecimal**| The sampling temperature, between 0 and 1. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. If set to 0, the model will use [log probability](https://en.wikipedia.org/wiki/Log_probability) to automatically increase the temperature until certain thresholds are hit.  | [optional] [default to 0] |
| **include\[\]** | [**List**](../Models/TranscriptionInclude.md)| Additional information to include in the transcription response.  &#x60;logprobs&#x60; will return the log probabilities of the tokens in the  response to understand the model&#39;s confidence in the transcription.  &#x60;logprobs&#x60; only works with response_format set to &#x60;json&#x60; and only with  the models &#x60;gpt-4o-transcribe&#x60; and &#x60;gpt-4o-mini-transcribe&#x60;.  | [optional] [default to null] |
| **timestamp\_granularities\[\]** | [**List**](../Models/String.md)| The timestamp granularities to populate for this transcription. &#x60;response_format&#x60; must be set &#x60;verbose_json&#x60; to use timestamp granularities. Either or both of these options are supported: &#x60;word&#x60;, or &#x60;segment&#x60;. Note: There is no additional latency for segment timestamps, but generating word timestamps incurs additional latency.  | [optional] [default to null] [enum: word, segment] |
| **stream** | **Boolean**| If set to true, the model response data will be streamed to the client as it is generated using [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).  See the [Streaming section of the Speech-to-Text guide](/docs/guides/speech-to-text?lang&#x3D;curl#streaming-transcriptions) for more information.  Note: Streaming is not supported for the &#x60;whisper-1&#x60; model and will be ignored.  | [optional] [default to false] |

### Return type

[**createTranscription_200_response**](../Models/createTranscription_200_response.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: multipart/form-data
- **Accept**: application/json, text/event-stream

<a name="createTranslation"></a>
# **createTranslation**
> createTranslation_200_response createTranslation(file, model, prompt, response\_format, temperature)

Translates audio into English.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **file** | **File**| The audio file object (not file name) translate, in one of these formats: flac, mp3, mp4, mpeg, mpga, m4a, ogg, wav, or webm.  | [default to null] |
| **model** | [**CreateTranslationRequest_model**](../Models/CreateTranslationRequest_model.md)|  | [default to null] |
| **prompt** | **String**| An optional text to guide the model&#39;s style or continue a previous audio segment. The [prompt](/docs/guides/speech-to-text#prompting) should be in English.  | [optional] [default to null] |
| **response\_format** | **String**| The format of the output, in one of these options: &#x60;json&#x60;, &#x60;text&#x60;, &#x60;srt&#x60;, &#x60;verbose_json&#x60;, or &#x60;vtt&#x60;.  | [optional] [default to json] [enum: json, text, srt, verbose_json, vtt] |
| **temperature** | **BigDecimal**| The sampling temperature, between 0 and 1. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. If set to 0, the model will use [log probability](https://en.wikipedia.org/wiki/Log_probability) to automatically increase the temperature until certain thresholds are hit.  | [optional] [default to 0] |

### Return type

[**createTranslation_200_response**](../Models/createTranslation_200_response.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: multipart/form-data
- **Accept**: application/json

