# EvalRunOutputItem_sample
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **input** | [**List**](EvalRunOutputItem_sample_input_inner.md) | An array of input messages. | [default to null] |
| **output** | [**List**](EvalRunOutputItem_sample_output_inner.md) | An array of output messages. | [default to null] |
| **finish\_reason** | **String** | The reason why the sample generation was finished. | [default to null] |
| **model** | **String** | The model used for generating the sample. | [default to null] |
| **usage** | [**EvalRunOutputItem_sample_usage**](EvalRunOutputItem_sample_usage.md) |  | [default to null] |
| **error** | [**EvalApiError**](EvalApiError.md) |  | [default to null] |
| **temperature** | **BigDecimal** | The sampling temperature used. | [default to null] |
| **max\_completion\_tokens** | **Integer** | The maximum number of tokens allowed for completion. | [default to null] |
| **top\_p** | **BigDecimal** | The top_p value used for sampling. | [default to null] |
| **seed** | **Integer** | The seed used for generating the sample. | [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

