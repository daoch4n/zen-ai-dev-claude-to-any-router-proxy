# FunctionTool
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **type** | **String** | The type of the function tool. Always &#x60;function&#x60;. | [default to function] |
| **name** | **String** | The name of the function to call. | [default to null] |
| **description** | **String** | A description of the function. Used by the model to determine whether or not to call the function. | [optional] [default to null] |
| **parameters** | [**Map**](AnyType.md) | A JSON schema object describing the parameters of the function. | [default to null] |
| **strict** | **Boolean** | Whether to enforce strict parameter validation. Default &#x60;true&#x60;. | [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

