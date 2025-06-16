# Generation
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **id** | **String** | Generation ID | [optional] [default to null] |
| **model** | **String** | Model used | [optional] [default to null] |
| **streamed** | **Boolean** | Whether response was streamed | [optional] [default to null] |
| **generation\_time** | **BigDecimal** | Time taken to generate response | [optional] [default to null] |
| **created\_at** | **Date** |  | [optional] [default to null] |
| **tokens\_prompt** | **Integer** | Number of prompt tokens (native count) | [optional] [default to null] |
| **tokens\_completion** | **Integer** | Number of completion tokens (native count) | [optional] [default to null] |
| **native\_tokens\_prompt** | **Integer** | Native prompt token count | [optional] [default to null] |
| **native\_tokens\_completion** | **Integer** | Native completion token count | [optional] [default to null] |
| **num\_media** | **Integer** | Number of media items processed | [optional] [default to null] |
| **provider\_name** | **String** | Provider used for generation | [optional] [default to null] |
| **moderated** | **Boolean** | Whether content was moderated | [optional] [default to null] |
| **usage** | **BigDecimal** | Cost in USD | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

