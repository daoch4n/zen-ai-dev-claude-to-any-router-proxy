# CreateEvalLabelModelGrader
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **type** | **String** | The object type, which is always &#x60;label_model&#x60;. | [default to null] |
| **name** | **String** | The name of the grader. | [default to null] |
| **model** | **String** | The model to use for the evaluation. Must support structured outputs. | [default to null] |
| **input** | [**List**](CreateEvalItem.md) | A list of chat messages forming the prompt or context. May include variable references to the \&quot;item\&quot; namespace, ie {{item.name}}. | [default to null] |
| **labels** | **List** | The labels to classify to each item in the evaluation. | [default to null] |
| **passing\_labels** | **List** | The labels that indicate a passing result. Must be a subset of labels. | [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

