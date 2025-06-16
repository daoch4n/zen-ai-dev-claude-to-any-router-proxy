# Content
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **type** | **String** | The type of the input item. Always &#x60;input_file&#x60;. | [default to input_file] |
| **text** | **String** | The text output from the model. | [default to null] |
| **image\_url** | **String** | The URL of the image to be sent to the model. A fully qualified URL or base64 encoded image in a data URL. | [optional] [default to null] |
| **file\_id** | **String** | The ID of the file to be sent to the model. | [optional] [default to null] |
| **detail** | **String** | The detail level of the image to be sent to the model. One of &#x60;high&#x60;, &#x60;low&#x60;, or &#x60;auto&#x60;. Defaults to &#x60;auto&#x60;. | [default to null] |
| **filename** | **String** | The name of the file to be sent to the model. | [optional] [default to null] |
| **file\_data** | **String** | The content of the file to be sent to the model.  | [optional] [default to null] |
| **annotations** | [**List**](Annotation.md) | The annotations of the text output. | [default to null] |
| **refusal** | **String** | The refusal explanationfrom the model. | [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

