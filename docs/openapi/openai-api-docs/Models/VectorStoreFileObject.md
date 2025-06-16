# VectorStoreFileObject
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **id** | **String** | The identifier, which can be referenced in API endpoints. | [default to null] |
| **object** | **String** | The object type, which is always &#x60;vector_store.file&#x60;. | [default to null] |
| **usage\_bytes** | **Integer** | The total vector store usage in bytes. Note that this may be different from the original file size. | [default to null] |
| **created\_at** | **Integer** | The Unix timestamp (in seconds) for when the vector store file was created. | [default to null] |
| **vector\_store\_id** | **String** | The ID of the [vector store](/docs/api-reference/vector-stores/object) that the [File](/docs/api-reference/files) is attached to. | [default to null] |
| **status** | **String** | The status of the vector store file, which can be either &#x60;in_progress&#x60;, &#x60;completed&#x60;, &#x60;cancelled&#x60;, or &#x60;failed&#x60;. The status &#x60;completed&#x60; indicates that the vector store file is ready for use. | [default to null] |
| **last\_error** | [**VectorStoreFileObject_last_error**](VectorStoreFileObject_last_error.md) |  | [default to null] |
| **chunking\_strategy** | [**VectorStoreFileObject_chunking_strategy**](VectorStoreFileObject_chunking_strategy.md) |  | [optional] [default to null] |
| **attributes** | [**Map**](VectorStoreFileAttributes_value.md) | Set of 16 key-value pairs that can be attached to an object. This can be  useful for storing additional information about the object in a structured  format, and querying for objects via API or the dashboard. Keys are strings  with a maximum length of 64 characters. Values are strings with a maximum  length of 512 characters, booleans, or numbers.  | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

