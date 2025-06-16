# VectorStoreSearchRequest
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **query** | [**VectorStoreSearchRequest_query**](VectorStoreSearchRequest_query.md) |  | [default to null] |
| **rewrite\_query** | **Boolean** | Whether to rewrite the natural language query for vector search. | [optional] [default to false] |
| **max\_num\_results** | **Integer** | The maximum number of results to return. This number should be between 1 and 50 inclusive. | [optional] [default to 10] |
| **filters** | [**VectorStoreSearchRequest_filters**](VectorStoreSearchRequest_filters.md) |  | [optional] [default to null] |
| **ranking\_options** | [**VectorStoreSearchRequest_ranking_options**](VectorStoreSearchRequest_ranking_options.md) |  | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

