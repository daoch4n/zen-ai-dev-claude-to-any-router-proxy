# FileSearchToolCall
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **id** | **String** | The unique ID of the file search tool call.  | [default to null] |
| **type** | **String** | The type of the file search tool call. Always &#x60;file_search_call&#x60;.  | [default to null] |
| **status** | **String** | The status of the file search tool call. One of &#x60;in_progress&#x60;,  &#x60;searching&#x60;, &#x60;incomplete&#x60; or &#x60;failed&#x60;,  | [default to null] |
| **queries** | **List** | The queries used to search for files.  | [default to null] |
| **results** | [**List**](FileSearchToolCall_results_inner.md) | The results of the file search tool call.  | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

