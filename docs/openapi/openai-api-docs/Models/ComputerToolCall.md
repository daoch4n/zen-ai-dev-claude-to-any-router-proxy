# ComputerToolCall
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **type** | **String** | The type of the computer call. Always &#x60;computer_call&#x60;. | [default to computer_call] |
| **id** | **String** | The unique ID of the computer call. | [default to null] |
| **call\_id** | **String** | An identifier used when responding to the tool call with output.  | [default to null] |
| **action** | [**ComputerAction**](ComputerAction.md) |  | [default to null] |
| **pending\_safety\_checks** | [**List**](ComputerToolCallSafetyCheck.md) | The pending safety checks for the computer call.  | [default to null] |
| **status** | **String** | The status of the item. One of &#x60;in_progress&#x60;, &#x60;completed&#x60;, or &#x60;incomplete&#x60;. Populated when items are returned via API.  | [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

