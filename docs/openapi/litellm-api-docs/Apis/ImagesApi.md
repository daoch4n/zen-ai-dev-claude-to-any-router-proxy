# ImagesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**imageEditApiImagesEditsPost**](ImagesApi.md#imageEditApiImagesEditsPost) | **POST** /images/edits | Image Edit Api |
| [**imageEditApiV1ImagesEditsPost**](ImagesApi.md#imageEditApiV1ImagesEditsPost) | **POST** /v1/images/edits | Image Edit Api |
| [**imageGenerationImagesGenerationsPost**](ImagesApi.md#imageGenerationImagesGenerationsPost) | **POST** /images/generations | Image Generation |
| [**imageGenerationV1ImagesGenerationsPost**](ImagesApi.md#imageGenerationV1ImagesGenerationsPost) | **POST** /v1/images/generations | Image Generation |


<a name="imageEditApiImagesEditsPost"></a>
# **imageEditApiImagesEditsPost**
> oas_any_type_not_mapped imageEditApiImagesEditsPost(image, mask)

Image Edit Api

    Follows the OpenAI Images API spec: https://platform.openai.com/docs/api-reference/images/create  &#x60;&#x60;&#x60;bash curl -s -D &gt;(grep -i x-request-id &gt;&amp;2)     -o &gt;(jq -r &#39;.data[0].b64_json&#39; | base64 --decode &gt; gift-basket.png)     -X POST \&quot;http://localhost:4000/v1/images/edits\&quot;     -H \&quot;Authorization: Bearer sk-1234\&quot;         -F \&quot;model&#x3D;gpt-image-1\&quot;         -F \&quot;image[]&#x3D;@soap.png\&quot;         -F &#39;prompt&#x3D;Create a studio ghibli image of this&#39; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **image** | **List**|  | [default to null] |
| **mask** | **List**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: multipart/form-data
- **Accept**: application/json

<a name="imageEditApiV1ImagesEditsPost"></a>
# **imageEditApiV1ImagesEditsPost**
> oas_any_type_not_mapped imageEditApiV1ImagesEditsPost(image, mask)

Image Edit Api

    Follows the OpenAI Images API spec: https://platform.openai.com/docs/api-reference/images/create  &#x60;&#x60;&#x60;bash curl -s -D &gt;(grep -i x-request-id &gt;&amp;2)     -o &gt;(jq -r &#39;.data[0].b64_json&#39; | base64 --decode &gt; gift-basket.png)     -X POST \&quot;http://localhost:4000/v1/images/edits\&quot;     -H \&quot;Authorization: Bearer sk-1234\&quot;         -F \&quot;model&#x3D;gpt-image-1\&quot;         -F \&quot;image[]&#x3D;@soap.png\&quot;         -F &#39;prompt&#x3D;Create a studio ghibli image of this&#39; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **image** | **List**|  | [default to null] |
| **mask** | **List**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: multipart/form-data
- **Accept**: application/json

<a name="imageGenerationImagesGenerationsPost"></a>
# **imageGenerationImagesGenerationsPost**
> oas_any_type_not_mapped imageGenerationImagesGenerationsPost()

Image Generation

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="imageGenerationV1ImagesGenerationsPost"></a>
# **imageGenerationV1ImagesGenerationsPost**
> oas_any_type_not_mapped imageGenerationV1ImagesGenerationsPost()

Image Generation

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

