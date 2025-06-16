# CreateEvalCustomDataSourceConfig
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **type** | **String** | The type of data source. Always &#x60;custom&#x60;. | [default to custom] |
| **item\_schema** | [**Map**](AnyType.md) | The json schema for each row in the data source. | [default to null] |
| **include\_sample\_schema** | **Boolean** | Whether the eval should expect you to populate the sample namespace (ie, by generating responses off of your data source) | [optional] [default to false] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

