# CreateVectorStoreRequest
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **file\_ids** | **List** | A list of [File](/docs/api-reference/files) IDs that the vector store should use. Useful for tools like &#x60;file_search&#x60; that can access files. | [optional] [default to null] |
| **name** | **String** | The name of the vector store. | [optional] [default to null] |
| **expires\_after** | [**VectorStoreExpirationAfter**](VectorStoreExpirationAfter.md) |  | [optional] [default to null] |
| **chunking\_strategy** | [**CreateVectorStoreRequest_chunking_strategy**](CreateVectorStoreRequest_chunking_strategy.md) |  | [optional] [default to null] |
| **metadata** | **Map** | Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard.   Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.  | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

