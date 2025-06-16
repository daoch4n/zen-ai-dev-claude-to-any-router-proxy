# EvalScoreModelGrader
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **type** | **String** | The object type, which is always &#x60;score_model&#x60;. | [default to null] |
| **name** | **String** | The name of the grader. | [default to null] |
| **model** | **String** | The model to use for the evaluation. | [default to null] |
| **sampling\_params** | [**Object**](.md) | The sampling parameters for the model. | [optional] [default to null] |
| **input** | [**List**](EvalItem.md) | The input text. This may include template strings. | [default to null] |
| **pass\_threshold** | **BigDecimal** | The threshold for the score. | [optional] [default to null] |
| **range** | **List** | The range of the score. Defaults to &#x60;[0, 1]&#x60;. | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

