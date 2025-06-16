# OutputItem
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **id** | **String** | The unique identifier of the reasoning content.  | [default to null] |
| **type** | **String** | The type of the output message. Always &#x60;message&#x60;.  | [default to null] |
| **role** | **String** | The role of the output message. Always &#x60;assistant&#x60;.  | [default to null] |
| **content** | [**List**](OutputContent.md) | The content of the output message.  | [default to null] |
| **status** | **String** | The status of the item. One of &#x60;in_progress&#x60;, &#x60;completed&#x60;, or &#x60;incomplete&#x60;. Populated when items are returned via API.  | [default to null] |
| **queries** | **List** | The queries used to search for files.  | [default to null] |
| **results** | [**List**](FileSearchToolCall_results_inner.md) | The results of the file search tool call.  | [optional] [default to null] |
| **call\_id** | **String** | An identifier used when responding to the tool call with output.  | [default to null] |
| **name** | **String** | The name of the function to run.  | [default to null] |
| **arguments** | **String** | A JSON string of the arguments to pass to the function.  | [default to null] |
| **action** | [**ComputerAction**](ComputerAction.md) |  | [default to null] |
| **pending\_safety\_checks** | [**List**](ComputerToolCallSafetyCheck.md) | The pending safety checks for the computer call.  | [default to null] |
| **summary** | [**List**](ReasoningItem_summary_inner.md) | Reasoning text contents.  | [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

