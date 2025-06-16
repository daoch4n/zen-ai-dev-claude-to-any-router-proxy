# ComputerToolCallOutputResource
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **type** | **String** | The type of the computer tool call output. Always &#x60;computer_call_output&#x60;.  | [default to computer_call_output] |
| **id** | **String** | The unique ID of the computer call tool output.  | [default to null] |
| **call\_id** | **String** | The ID of the computer tool call that produced the output.  | [default to null] |
| **acknowledged\_safety\_checks** | [**List**](ComputerToolCallSafetyCheck.md) | The safety checks reported by the API that have been acknowledged by the  developer.  | [optional] [default to null] |
| **output** | [**ComputerScreenshotImage**](ComputerScreenshotImage.md) |  | [default to null] |
| **status** | **String** | The status of the message input. One of &#x60;in_progress&#x60;, &#x60;completed&#x60;, or &#x60;incomplete&#x60;. Populated when input items are returned via API.  | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

