# Image
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **b64\_json** | **String** | The base64-encoded JSON of the generated image. Default value for &#x60;gpt-image-1&#x60;, and only present if &#x60;response_format&#x60; is set to &#x60;b64_json&#x60; for &#x60;dall-e-2&#x60; and &#x60;dall-e-3&#x60;. | [optional] [default to null] |
| **url** | **String** | When using &#x60;dall-e-2&#x60; or &#x60;dall-e-3&#x60;, the URL of the generated image if &#x60;response_format&#x60; is set to &#x60;url&#x60; (default value). Unsupported for &#x60;gpt-image-1&#x60;. | [optional] [default to null] |
| **revised\_prompt** | **String** | For &#x60;dall-e-3&#x60; only, the revised prompt that was used to generate the image. | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

