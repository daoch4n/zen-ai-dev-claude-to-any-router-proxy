# ImagesApi

All URIs are relative to *https://api.openai.com/v1*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createImage**](ImagesApi.md#createImage) | **POST** /images/generations | Creates an image given a prompt. [Learn more](/docs/guides/images).  |
| [**createImageEdit**](ImagesApi.md#createImageEdit) | **POST** /images/edits | Creates an edited or extended image given one or more source images and a prompt. This endpoint only supports &#x60;gpt-image-1&#x60; and &#x60;dall-e-2&#x60;. |
| [**createImageVariation**](ImagesApi.md#createImageVariation) | **POST** /images/variations | Creates a variation of a given image. This endpoint only supports &#x60;dall-e-2&#x60;. |


<a name="createImage"></a>
# **createImage**
> ImagesResponse createImage(CreateImageRequest)

Creates an image given a prompt. [Learn more](/docs/guides/images). 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **CreateImageRequest** | [**CreateImageRequest**](../Models/CreateImageRequest.md)|  | |

### Return type

[**ImagesResponse**](../Models/ImagesResponse.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="createImageEdit"></a>
# **createImageEdit**
> ImagesResponse createImageEdit(image, prompt, mask, model, n, size, response\_format, user, quality)

Creates an edited or extended image given one or more source images and a prompt. This endpoint only supports &#x60;gpt-image-1&#x60; and &#x60;dall-e-2&#x60;.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **image** | [**CreateImageEditRequest_image**](../Models/CreateImageEditRequest_image.md)|  | [default to null] |
| **prompt** | **String**| A text description of the desired image(s). The maximum length is 1000 characters for &#x60;dall-e-2&#x60;, and 32000 characters for &#x60;gpt-image-1&#x60;. | [default to null] |
| **mask** | **File**| An additional image whose fully transparent areas (e.g. where alpha is zero) indicate where &#x60;image&#x60; should be edited. If there are multiple images provided, the mask will be applied on the first image. Must be a valid PNG file, less than 4MB, and have the same dimensions as &#x60;image&#x60;. | [optional] [default to null] |
| **model** | [**CreateImageEditRequest_model**](../Models/CreateImageEditRequest_model.md)|  | [optional] [default to null] |
| **n** | **Integer**| The number of images to generate. Must be between 1 and 10. | [optional] [default to 1] |
| **size** | **String**| The size of the generated images. Must be one of &#x60;1024x1024&#x60;, &#x60;1536x1024&#x60; (landscape), &#x60;1024x1536&#x60; (portrait), or &#x60;auto&#x60; (default value) for &#x60;gpt-image-1&#x60;, and one of &#x60;256x256&#x60;, &#x60;512x512&#x60;, or &#x60;1024x1024&#x60; for &#x60;dall-e-2&#x60;. | [optional] [default to 1024x1024] [enum: 256x256, 512x512, 1024x1024, 1536x1024, 1024x1536, auto] |
| **response\_format** | **String**| The format in which the generated images are returned. Must be one of &#x60;url&#x60; or &#x60;b64_json&#x60;. URLs are only valid for 60 minutes after the image has been generated. This parameter is only supported for &#x60;dall-e-2&#x60;, as &#x60;gpt-image-1&#x60; will always return base64-encoded images. | [optional] [default to url] [enum: url, b64_json] |
| **user** | **String**| A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse. [Learn more](/docs/guides/safety-best-practices#end-user-ids).  | [optional] [default to null] |
| **quality** | **String**| The quality of the image that will be generated. &#x60;high&#x60;, &#x60;medium&#x60; and &#x60;low&#x60; are only supported for &#x60;gpt-image-1&#x60;. &#x60;dall-e-2&#x60; only supports &#x60;standard&#x60; quality. Defaults to &#x60;auto&#x60;.  | [optional] [default to auto] [enum: standard, low, medium, high, auto] |

### Return type

[**ImagesResponse**](../Models/ImagesResponse.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: multipart/form-data
- **Accept**: application/json

<a name="createImageVariation"></a>
# **createImageVariation**
> ImagesResponse createImageVariation(image, model, n, response\_format, size, user)

Creates a variation of a given image. This endpoint only supports &#x60;dall-e-2&#x60;.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **image** | **File**| The image to use as the basis for the variation(s). Must be a valid PNG file, less than 4MB, and square. | [default to null] |
| **model** | [**CreateImageVariationRequest_model**](../Models/CreateImageVariationRequest_model.md)|  | [optional] [default to null] |
| **n** | **Integer**| The number of images to generate. Must be between 1 and 10. | [optional] [default to 1] |
| **response\_format** | **String**| The format in which the generated images are returned. Must be one of &#x60;url&#x60; or &#x60;b64_json&#x60;. URLs are only valid for 60 minutes after the image has been generated. | [optional] [default to url] [enum: url, b64_json] |
| **size** | **String**| The size of the generated images. Must be one of &#x60;256x256&#x60;, &#x60;512x512&#x60;, or &#x60;1024x1024&#x60;. | [optional] [default to 1024x1024] [enum: 256x256, 512x512, 1024x1024] |
| **user** | **String**| A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse. [Learn more](/docs/guides/safety-best-practices#end-user-ids).  | [optional] [default to null] |

### Return type

[**ImagesResponse**](../Models/ImagesResponse.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: multipart/form-data
- **Accept**: application/json

