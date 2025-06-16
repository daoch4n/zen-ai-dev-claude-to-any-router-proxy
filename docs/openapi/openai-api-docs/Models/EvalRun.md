# EvalRun
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **object** | **String** | The type of the object. Always \&quot;eval.run\&quot;. | [default to eval.run] |
| **id** | **String** | Unique identifier for the evaluation run. | [default to null] |
| **eval\_id** | **String** | The identifier of the associated evaluation. | [default to null] |
| **status** | **String** | The status of the evaluation run. | [default to null] |
| **model** | **String** | The model that is evaluated, if applicable. | [default to null] |
| **name** | **String** | The name of the evaluation run. | [default to null] |
| **created\_at** | **Integer** | Unix timestamp (in seconds) when the evaluation run was created. | [default to null] |
| **report\_url** | **String** | The URL to the rendered evaluation run report on the UI dashboard. | [default to null] |
| **result\_counts** | [**EvalRun_result_counts**](EvalRun_result_counts.md) |  | [default to null] |
| **per\_model\_usage** | [**List**](EvalRun_per_model_usage_inner.md) | Usage statistics for each model during the evaluation run. | [default to null] |
| **per\_testing\_criteria\_results** | [**List**](EvalRun_per_testing_criteria_results_inner.md) | Results per testing criteria applied during the evaluation run. | [default to null] |
| **data\_source** | [**EvalRun_data_source**](EvalRun_data_source.md) |  | [default to null] |
| **metadata** | **Map** | Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard.   Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.  | [default to null] |
| **error** | [**EvalApiError**](EvalApiError.md) |  | [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

