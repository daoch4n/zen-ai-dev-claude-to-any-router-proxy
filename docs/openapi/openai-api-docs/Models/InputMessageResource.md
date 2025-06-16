# InputMessageResource
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **type** | **String** | The type of the message input. Always set to &#x60;message&#x60;.  | [optional] [default to null] |
| **role** | **String** | The role of the message input. One of &#x60;user&#x60;, &#x60;system&#x60;, or &#x60;developer&#x60;.  | [default to null] |
| **status** | **String** | The status of item. One of &#x60;in_progress&#x60;, &#x60;completed&#x60;, or &#x60;incomplete&#x60;. Populated when items are returned via API.  | [optional] [default to null] |
| **content** | [**List**](InputContent.md) | A list of one or many input items to the model, containing different content  types.  | [default to null] |
| **id** | **String** | The unique ID of the message input.  | [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

