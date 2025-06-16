# Tool
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **type** | **String** | The type of the file search tool. Always &#x60;file_search&#x60;. | [default to file_search] |
| **vector\_store\_ids** | **List** | The IDs of the vector stores to search. | [default to null] |
| **max\_num\_results** | **Integer** | The maximum number of results to return. This number should be between 1 and 50 inclusive. | [optional] [default to null] |
| **ranking\_options** | [**RankingOptions**](RankingOptions.md) |  | [optional] [default to null] |
| **filters** | [**Filters**](Filters.md) |  | [optional] [default to null] |
| **name** | **String** | The name of the function to call. | [default to null] |
| **description** | **String** | A description of the function. Used by the model to determine whether or not to call the function. | [optional] [default to null] |
| **parameters** | **Map** | A JSON schema object describing the parameters of the function. | [default to null] |
| **strict** | **Boolean** | Whether to enforce strict parameter validation. Default &#x60;true&#x60;. | [default to null] |
| **user\_location** | [**ApproximateLocation**](ApproximateLocation.md) |  | [optional] [default to null] |
| **search\_context\_size** | **String** | High level guidance for the amount of context window space to use for the search. One of &#x60;low&#x60;, &#x60;medium&#x60;, or &#x60;high&#x60;. &#x60;medium&#x60; is the default. | [optional] [default to null] |
| **environment** | **String** | The type of computer environment to control. | [default to null] |
| **display\_width** | **Integer** | The width of the computer display. | [default to null] |
| **display\_height** | **Integer** | The height of the computer display. | [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

