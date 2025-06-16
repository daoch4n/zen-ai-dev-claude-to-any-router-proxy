# FileSearchTool
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **type** | **String** | The type of the file search tool. Always &#x60;file_search&#x60;. | [default to file_search] |
| **vector\_store\_ids** | **List** | The IDs of the vector stores to search. | [default to null] |
| **max\_num\_results** | **Integer** | The maximum number of results to return. This number should be between 1 and 50 inclusive. | [optional] [default to null] |
| **ranking\_options** | [**RankingOptions**](RankingOptions.md) |  | [optional] [default to null] |
| **filters** | [**Filters**](Filters.md) |  | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

