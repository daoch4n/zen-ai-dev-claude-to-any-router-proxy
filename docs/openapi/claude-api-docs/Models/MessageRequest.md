# MessageRequest
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **model** | **String** | The Claude model to use | [default to null] |
| **messages** | [**List**](Message.md) | The conversation messages | [default to null] |
| **max\_tokens** | **Integer** | Maximum tokens to generate | [default to null] |
| **temperature** | **BigDecimal** | Sampling temperature (0-1) | [optional] [default to null] |
| **top\_p** | **BigDecimal** | Top-p sampling parameter | [optional] [default to null] |
| **top\_k** | **Integer** | Top-k sampling parameter | [optional] [default to null] |
| **stop\_sequences** | **List** | Sequences that will stop generation | [optional] [default to null] |
| **stream** | **Boolean** | Whether to stream the response | [optional] [default to false] |
| **system** | **String** | System message for context | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

