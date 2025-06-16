# CompletionResponse
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **type** | **String** | Object type.  For Text Completions, this is always &#x60;\&quot;completion\&quot;&#x60;. | [default to completion] |
| **id** | **String** | Unique object identifier.  The format and length of IDs may change over time. | [default to null] |
| **completion** | **String** | The resulting completion up to and excluding the stop sequences. | [default to null] |
| **stop\_reason** | **String** |  | [default to null] |
| **model** | [**Model**](Model.md) |  | [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

