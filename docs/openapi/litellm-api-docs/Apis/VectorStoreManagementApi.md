# VectorStoreManagementApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**deleteVectorStoreVectorStoreDeletePost**](VectorStoreManagementApi.md#deleteVectorStoreVectorStoreDeletePost) | **POST** /vector_store/delete | Delete Vector Store |
| [**listVectorStoresVectorStoreListGet**](VectorStoreManagementApi.md#listVectorStoresVectorStoreListGet) | **GET** /vector_store/list | List Vector Stores |
| [**newVectorStoreVectorStoreNewPost**](VectorStoreManagementApi.md#newVectorStoreVectorStoreNewPost) | **POST** /vector_store/new | New Vector Store |


<a name="deleteVectorStoreVectorStoreDeletePost"></a>
# **deleteVectorStoreVectorStoreDeletePost**
> oas_any_type_not_mapped deleteVectorStoreVectorStoreDeletePost(VectorStoreDeleteRequest)

Delete Vector Store

    Delete a vector store.  Parameters: - vector_store_id: str - ID of the vector store to delete

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **VectorStoreDeleteRequest** | [**VectorStoreDeleteRequest**](../Models/VectorStoreDeleteRequest.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="listVectorStoresVectorStoreListGet"></a>
# **listVectorStoresVectorStoreListGet**
> LiteLLM_ManagedVectorStoreListResponse listVectorStoresVectorStoreListGet(page, page\_size)

List Vector Stores

    List all available vector stores with optional filtering and pagination. Combines both in-memory vector stores and those stored in the database.  Parameters: - page: int - Page number for pagination (default: 1) - page_size: int - Number of items per page (default: 100)

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **page** | **Integer**|  | [optional] [default to 1] |
| **page\_size** | **Integer**|  | [optional] [default to 100] |

### Return type

[**LiteLLM_ManagedVectorStoreListResponse**](../Models/LiteLLM_ManagedVectorStoreListResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="newVectorStoreVectorStoreNewPost"></a>
# **newVectorStoreVectorStoreNewPost**
> oas_any_type_not_mapped newVectorStoreVectorStoreNewPost(LiteLLM\_ManagedVectorStore)

New Vector Store

    Create a new vector store.  Parameters: - vector_store_id: str - Unique identifier for the vector store - custom_llm_provider: str - Provider of the vector store - vector_store_name: Optional[str] - Name of the vector store - vector_store_description: Optional[str] - Description of the vector store - vector_store_metadata: Optional[Dict] - Additional metadata for the vector store

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **LiteLLM\_ManagedVectorStore** | [**LiteLLM_ManagedVectorStore**](../Models/LiteLLM_ManagedVectorStore.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

