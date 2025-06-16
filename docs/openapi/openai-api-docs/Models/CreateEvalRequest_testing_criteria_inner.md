# CreateEvalRequest_testing_criteria_inner
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **type** | **String** | The object type, which is always &#x60;label_model&#x60;. | [default to null] |
| **name** | **String** | The name of the grader. | [default to null] |
| **model** | **String** | The model to use for the evaluation. | [default to null] |
| **input** | [**List**](EvalItem.md) | The input text. This may include template strings. | [default to null] |
| **labels** | **List** | The labels to classify to each item in the evaluation. | [default to null] |
| **passing\_labels** | **List** | The labels that indicate a passing result. Must be a subset of labels. | [default to null] |
| **reference** | **String** | The text being graded against. | [default to null] |
| **operation** | **String** | The string check operation to perform. One of &#x60;eq&#x60;, &#x60;ne&#x60;, &#x60;like&#x60;, or &#x60;ilike&#x60;. | [default to null] |
| **pass\_threshold** | **BigDecimal** | The threshold for the score. | [default to null] |
| **evaluation\_metric** | **String** | The evaluation metric to use. One of &#x60;fuzzy_match&#x60;, &#x60;bleu&#x60;, &#x60;gleu&#x60;, &#x60;meteor&#x60;, &#x60;rouge_1&#x60;, &#x60;rouge_2&#x60;, &#x60;rouge_3&#x60;, &#x60;rouge_4&#x60;, &#x60;rouge_5&#x60;, or &#x60;rouge_l&#x60;. | [default to null] |
| **source** | **String** | The source code of the python script. | [default to null] |
| **image\_tag** | **String** | The image tag to use for the python script. | [optional] [default to null] |
| **sampling\_params** | [**Object**](.md) | The sampling parameters for the model. | [optional] [default to null] |
| **range** | **List** | The range of the score. Defaults to &#x60;[0, 1]&#x60;. | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

