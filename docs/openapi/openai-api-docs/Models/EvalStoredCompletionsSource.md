# EvalStoredCompletionsSource
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **type** | **String** | The type of source. Always &#x60;stored_completions&#x60;. | [default to stored_completions] |
| **metadata** | **Map** | Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard.   Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.  | [optional] [default to null] |
| **model** | **String** | An optional model to filter by (e.g., &#39;gpt-4o&#39;). | [optional] [default to null] |
| **created\_after** | **Integer** | An optional Unix timestamp to filter items created after this time. | [optional] [default to null] |
| **created\_before** | **Integer** | An optional Unix timestamp to filter items created before this time. | [optional] [default to null] |
| **limit** | **Integer** | An optional maximum number of items to return. | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

