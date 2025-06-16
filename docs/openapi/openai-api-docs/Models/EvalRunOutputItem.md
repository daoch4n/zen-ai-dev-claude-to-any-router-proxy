# EvalRunOutputItem
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **object** | **String** | The type of the object. Always \&quot;eval.run.output_item\&quot;. | [default to eval.run.output_item] |
| **id** | **String** | Unique identifier for the evaluation run output item. | [default to null] |
| **run\_id** | **String** | The identifier of the evaluation run associated with this output item. | [default to null] |
| **eval\_id** | **String** | The identifier of the evaluation group. | [default to null] |
| **created\_at** | **Integer** | Unix timestamp (in seconds) when the evaluation run was created. | [default to null] |
| **status** | **String** | The status of the evaluation run. | [default to null] |
| **datasource\_item\_id** | **Integer** | The identifier for the data source item. | [default to null] |
| **datasource\_item** | [**Map**](AnyType.md) | Details of the input data source item. | [default to null] |
| **results** | [**List**](map.md) | A list of results from the evaluation run. | [default to null] |
| **sample** | [**EvalRunOutputItem_sample**](EvalRunOutputItem_sample.md) |  | [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

