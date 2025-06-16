# CreateEvalResponsesRunDataSource_source
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **type** | **String** | The type of jsonl source. Always &#x60;file_content&#x60;. | [default to file_content] |
| **content** | [**List**](EvalJsonlFileContentSource_content_inner.md) | The content of the jsonl file. | [default to null] |
| **id** | **String** | The identifier of the file. | [default to null] |
| **metadata** | [**Object**](.md) | Metadata filter for the responses. This is a query parameter used to select responses. | [optional] [default to null] |
| **model** | **String** | The name of the model to find responses for. This is a query parameter used to select responses. | [optional] [default to null] |
| **instructions\_search** | **String** | Optional search string for instructions. This is a query parameter used to select responses. | [optional] [default to null] |
| **created\_after** | **Integer** | Only include items created after this timestamp (inclusive). This is a query parameter used to select responses. | [optional] [default to null] |
| **created\_before** | **Integer** | Only include items created before this timestamp (inclusive). This is a query parameter used to select responses. | [optional] [default to null] |
| **has\_tool\_calls** | **Boolean** | Whether the response has tool calls. This is a query parameter used to select responses. | [optional] [default to null] |
| **reasoning\_effort** | [**ReasoningEffort**](ReasoningEffort.md) |  | [optional] [default to null] |
| **temperature** | **BigDecimal** | Sampling temperature. This is a query parameter used to select responses. | [optional] [default to null] |
| **top\_p** | **BigDecimal** | Nucleus sampling parameter. This is a query parameter used to select responses. | [optional] [default to null] |
| **users** | **List** | List of user identifiers. This is a query parameter used to select responses. | [optional] [default to null] |
| **allow\_parallel\_tool\_calls** | **Boolean** | Whether to allow parallel tool calls. This is a query parameter used to select responses. | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

