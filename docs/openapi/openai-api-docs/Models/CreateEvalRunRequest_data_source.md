# CreateEvalRunRequest_data_source
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **type** | **String** | The type of data source. Always &#x60;jsonl&#x60;. | [default to jsonl] |
| **source** | [**CreateEvalResponsesRunDataSource_source**](CreateEvalResponsesRunDataSource_source.md) |  | [default to null] |
| **input\_messages** | [**CreateEvalResponsesRunDataSource_input_messages**](CreateEvalResponsesRunDataSource_input_messages.md) |  | [optional] [default to null] |
| **sampling\_params** | [**CreateEvalCompletionsRunDataSource_sampling_params**](CreateEvalCompletionsRunDataSource_sampling_params.md) |  | [optional] [default to null] |
| **model** | **String** | The name of the model to use for generating completions (e.g. \&quot;o3-mini\&quot;). | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

