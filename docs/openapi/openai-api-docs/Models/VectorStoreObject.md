# VectorStoreObject
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **id** | **String** | The identifier, which can be referenced in API endpoints. | [default to null] |
| **object** | **String** | The object type, which is always &#x60;vector_store&#x60;. | [default to null] |
| **created\_at** | **Integer** | The Unix timestamp (in seconds) for when the vector store was created. | [default to null] |
| **name** | **String** | The name of the vector store. | [default to null] |
| **usage\_bytes** | **Integer** | The total number of bytes used by the files in the vector store. | [default to null] |
| **file\_counts** | [**VectorStoreObject_file_counts**](VectorStoreObject_file_counts.md) |  | [default to null] |
| **status** | **String** | The status of the vector store, which can be either &#x60;expired&#x60;, &#x60;in_progress&#x60;, or &#x60;completed&#x60;. A status of &#x60;completed&#x60; indicates that the vector store is ready for use. | [default to null] |
| **expires\_after** | [**VectorStoreExpirationAfter**](VectorStoreExpirationAfter.md) |  | [optional] [default to null] |
| **expires\_at** | **Integer** | The Unix timestamp (in seconds) for when the vector store will expire. | [optional] [default to null] |
| **last\_active\_at** | **Integer** | The Unix timestamp (in seconds) for when the vector store was last active. | [default to null] |
| **metadata** | **Map** | Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard.   Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.  | [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

