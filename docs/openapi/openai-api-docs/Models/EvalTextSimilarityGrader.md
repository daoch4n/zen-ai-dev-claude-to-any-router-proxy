# EvalTextSimilarityGrader
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **type** | **String** | The type of grader. | [default to text_similarity] |
| **name** | **String** | The name of the grader. | [optional] [default to null] |
| **input** | **String** | The text being graded. | [default to null] |
| **reference** | **String** | The text being graded against. | [default to null] |
| **pass\_threshold** | **BigDecimal** | A float score where a value greater than or equal indicates a passing grade. | [default to null] |
| **evaluation\_metric** | **String** | The evaluation metric to use. One of &#x60;fuzzy_match&#x60;, &#x60;bleu&#x60;, &#x60;gleu&#x60;, &#x60;meteor&#x60;, &#x60;rouge_1&#x60;, &#x60;rouge_2&#x60;, &#x60;rouge_3&#x60;, &#x60;rouge_4&#x60;, &#x60;rouge_5&#x60;, or &#x60;rouge_l&#x60;. | [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

