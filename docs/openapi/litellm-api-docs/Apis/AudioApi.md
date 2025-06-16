# AudioApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**audioSpeechAudioSpeechPost**](AudioApi.md#audioSpeechAudioSpeechPost) | **POST** /audio/speech | Audio Speech |
| [**audioSpeechV1AudioSpeechPost**](AudioApi.md#audioSpeechV1AudioSpeechPost) | **POST** /v1/audio/speech | Audio Speech |
| [**audioTranscriptionsAudioTranscriptionsPost**](AudioApi.md#audioTranscriptionsAudioTranscriptionsPost) | **POST** /audio/transcriptions | Audio Transcriptions |
| [**audioTranscriptionsV1AudioTranscriptionsPost**](AudioApi.md#audioTranscriptionsV1AudioTranscriptionsPost) | **POST** /v1/audio/transcriptions | Audio Transcriptions |


<a name="audioSpeechAudioSpeechPost"></a>
# **audioSpeechAudioSpeechPost**
> oas_any_type_not_mapped audioSpeechAudioSpeechPost()

Audio Speech

    Same params as:  https://platform.openai.com/docs/api-reference/audio/createSpeech

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="audioSpeechV1AudioSpeechPost"></a>
# **audioSpeechV1AudioSpeechPost**
> oas_any_type_not_mapped audioSpeechV1AudioSpeechPost()

Audio Speech

    Same params as:  https://platform.openai.com/docs/api-reference/audio/createSpeech

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="audioTranscriptionsAudioTranscriptionsPost"></a>
# **audioTranscriptionsAudioTranscriptionsPost**
> oas_any_type_not_mapped audioTranscriptionsAudioTranscriptionsPost(file)

Audio Transcriptions

    Same params as:  https://platform.openai.com/docs/api-reference/audio/createTranscription?lang&#x3D;curl

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **file** | **File**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: multipart/form-data
- **Accept**: application/json

<a name="audioTranscriptionsV1AudioTranscriptionsPost"></a>
# **audioTranscriptionsV1AudioTranscriptionsPost**
> oas_any_type_not_mapped audioTranscriptionsV1AudioTranscriptionsPost(file)

Audio Transcriptions

    Same params as:  https://platform.openai.com/docs/api-reference/audio/createTranscription?lang&#x3D;curl

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **file** | **File**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: multipart/form-data
- **Accept**: application/json

