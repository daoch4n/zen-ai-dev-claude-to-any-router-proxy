# RealtimeClientEvent
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **event\_id** | **String** | Optional client-generated ID used to identify this event. | [optional] [default to null] |
| **type** | **String** | The event type, must be &#x60;conversation.item.create&#x60;. | [default to null] |
| **previous\_item\_id** | **String** | The ID of the preceding item after which the new item will be inserted.  If not set, the new item will be appended to the end of the conversation. If set to &#x60;root&#x60;, the new item will be added to the beginning of the conversation. If set to an existing ID, it allows an item to be inserted mid-conversation. If the ID cannot be found, an error will be returned and the item will not be added.  | [optional] [default to null] |
| **item** | [**RealtimeConversationItem**](RealtimeConversationItem.md) |  | [default to null] |
| **item\_id** | **String** | The ID of the assistant message item to truncate. Only assistant message  items can be truncated.  | [default to null] |
| **content\_index** | **Integer** | The index of the content part to truncate. Set this to 0. | [default to null] |
| **audio\_end\_ms** | **Integer** | Inclusive duration up to which audio is truncated, in milliseconds. If  the audio_end_ms is greater than the actual audio duration, the server  will respond with an error.  | [default to null] |
| **audio** | **String** | Base64-encoded audio bytes. This must be in the format specified by the  &#x60;input_audio_format&#x60; field in the session configuration.  | [default to null] |
| **response\_id** | **String** | A specific response ID to cancel - if not provided, will cancel an  in-progress response in the default conversation.  | [optional] [default to null] |
| **response** | [**RealtimeResponseCreateParams**](RealtimeResponseCreateParams.md) |  | [optional] [default to null] |
| **session** | [**RealtimeTranscriptionSessionCreateRequest**](RealtimeTranscriptionSessionCreateRequest.md) |  | [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

