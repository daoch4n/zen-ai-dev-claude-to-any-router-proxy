# LlmUtilsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**supportedOpenaiParamsUtilsSupportedOpenaiParamsGet**](LlmUtilsApi.md#supportedOpenaiParamsUtilsSupportedOpenaiParamsGet) | **GET** /utils/supported_openai_params | Supported Openai Params |
| [**tokenCounterUtilsTokenCounterPost**](LlmUtilsApi.md#tokenCounterUtilsTokenCounterPost) | **POST** /utils/token_counter | Token Counter |
| [**transformRequestUtilsTransformRequestPost**](LlmUtilsApi.md#transformRequestUtilsTransformRequestPost) | **POST** /utils/transform_request | Transform Request |


<a name="supportedOpenaiParamsUtilsSupportedOpenaiParamsGet"></a>
# **supportedOpenaiParamsUtilsSupportedOpenaiParamsGet**
> oas_any_type_not_mapped supportedOpenaiParamsUtilsSupportedOpenaiParamsGet(model)

Supported Openai Params

    Returns supported openai params for a given litellm model name  e.g. &#x60;gpt-4&#x60; vs &#x60;gpt-3.5-turbo&#x60;  Example curl: &#x60;&#x60;&#x60; curl -X GET --location &#39;http://localhost:4000/utils/supported_openai_params?model&#x3D;gpt-3.5-turbo-16k&#39;         --header &#39;Authorization: Bearer sk-1234&#39; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **model** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="tokenCounterUtilsTokenCounterPost"></a>
# **tokenCounterUtilsTokenCounterPost**
> TokenCountResponse tokenCounterUtilsTokenCounterPost(TokenCountRequest)

Token Counter

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **TokenCountRequest** | [**TokenCountRequest**](../Models/TokenCountRequest.md)|  | |

### Return type

[**TokenCountResponse**](../Models/TokenCountResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="transformRequestUtilsTransformRequestPost"></a>
# **transformRequestUtilsTransformRequestPost**
> RawRequestTypedDict transformRequestUtilsTransformRequestPost(TransformRequestBody)

Transform Request

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **TransformRequestBody** | [**TransformRequestBody**](../Models/TransformRequestBody.md)|  | |

### Return type

[**RawRequestTypedDict**](../Models/RawRequestTypedDict.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

