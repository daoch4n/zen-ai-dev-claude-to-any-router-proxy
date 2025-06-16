# AssistantsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**addMessagesThreadsThreadIdMessagesPost**](AssistantsApi.md#addMessagesThreadsThreadIdMessagesPost) | **POST** /threads/{thread_id}/messages | Add Messages |
| [**addMessagesV1ThreadsThreadIdMessagesPost**](AssistantsApi.md#addMessagesV1ThreadsThreadIdMessagesPost) | **POST** /v1/threads/{thread_id}/messages | Add Messages |
| [**createAssistantAssistantsPost**](AssistantsApi.md#createAssistantAssistantsPost) | **POST** /assistants | Create Assistant |
| [**createAssistantV1AssistantsPost**](AssistantsApi.md#createAssistantV1AssistantsPost) | **POST** /v1/assistants | Create Assistant |
| [**createThreadsThreadsPost**](AssistantsApi.md#createThreadsThreadsPost) | **POST** /threads | Create Threads |
| [**createThreadsV1ThreadsPost**](AssistantsApi.md#createThreadsV1ThreadsPost) | **POST** /v1/threads | Create Threads |
| [**deleteAssistantAssistantsAssistantIdDelete**](AssistantsApi.md#deleteAssistantAssistantsAssistantIdDelete) | **DELETE** /assistants/{assistant_id} | Delete Assistant |
| [**deleteAssistantV1AssistantsAssistantIdDelete**](AssistantsApi.md#deleteAssistantV1AssistantsAssistantIdDelete) | **DELETE** /v1/assistants/{assistant_id} | Delete Assistant |
| [**getAssistantsAssistantsGet**](AssistantsApi.md#getAssistantsAssistantsGet) | **GET** /assistants | Get Assistants |
| [**getAssistantsV1AssistantsGet**](AssistantsApi.md#getAssistantsV1AssistantsGet) | **GET** /v1/assistants | Get Assistants |
| [**getMessagesThreadsThreadIdMessagesGet**](AssistantsApi.md#getMessagesThreadsThreadIdMessagesGet) | **GET** /threads/{thread_id}/messages | Get Messages |
| [**getMessagesV1ThreadsThreadIdMessagesGet**](AssistantsApi.md#getMessagesV1ThreadsThreadIdMessagesGet) | **GET** /v1/threads/{thread_id}/messages | Get Messages |
| [**getThreadThreadsThreadIdGet**](AssistantsApi.md#getThreadThreadsThreadIdGet) | **GET** /threads/{thread_id} | Get Thread |
| [**getThreadV1ThreadsThreadIdGet**](AssistantsApi.md#getThreadV1ThreadsThreadIdGet) | **GET** /v1/threads/{thread_id} | Get Thread |
| [**runThreadThreadsThreadIdRunsPost**](AssistantsApi.md#runThreadThreadsThreadIdRunsPost) | **POST** /threads/{thread_id}/runs | Run Thread |
| [**runThreadV1ThreadsThreadIdRunsPost**](AssistantsApi.md#runThreadV1ThreadsThreadIdRunsPost) | **POST** /v1/threads/{thread_id}/runs | Run Thread |


<a name="addMessagesThreadsThreadIdMessagesPost"></a>
# **addMessagesThreadsThreadIdMessagesPost**
> oas_any_type_not_mapped addMessagesThreadsThreadIdMessagesPost(thread\_id)

Add Messages

    Create a message.  API Reference - https://platform.openai.com/docs/api-reference/messages/createMessage

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **thread\_id** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="addMessagesV1ThreadsThreadIdMessagesPost"></a>
# **addMessagesV1ThreadsThreadIdMessagesPost**
> oas_any_type_not_mapped addMessagesV1ThreadsThreadIdMessagesPost(thread\_id)

Add Messages

    Create a message.  API Reference - https://platform.openai.com/docs/api-reference/messages/createMessage

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **thread\_id** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="createAssistantAssistantsPost"></a>
# **createAssistantAssistantsPost**
> oas_any_type_not_mapped createAssistantAssistantsPost()

Create Assistant

    Create assistant  API Reference docs - https://platform.openai.com/docs/api-reference/assistants/createAssistant

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="createAssistantV1AssistantsPost"></a>
# **createAssistantV1AssistantsPost**
> oas_any_type_not_mapped createAssistantV1AssistantsPost()

Create Assistant

    Create assistant  API Reference docs - https://platform.openai.com/docs/api-reference/assistants/createAssistant

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="createThreadsThreadsPost"></a>
# **createThreadsThreadsPost**
> oas_any_type_not_mapped createThreadsThreadsPost()

Create Threads

    Create a thread.  API Reference - https://platform.openai.com/docs/api-reference/threads/createThread

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="createThreadsV1ThreadsPost"></a>
# **createThreadsV1ThreadsPost**
> oas_any_type_not_mapped createThreadsV1ThreadsPost()

Create Threads

    Create a thread.  API Reference - https://platform.openai.com/docs/api-reference/threads/createThread

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="deleteAssistantAssistantsAssistantIdDelete"></a>
# **deleteAssistantAssistantsAssistantIdDelete**
> oas_any_type_not_mapped deleteAssistantAssistantsAssistantIdDelete(assistant\_id)

Delete Assistant

    Delete assistant  API Reference docs - https://platform.openai.com/docs/api-reference/assistants/createAssistant

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **assistant\_id** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="deleteAssistantV1AssistantsAssistantIdDelete"></a>
# **deleteAssistantV1AssistantsAssistantIdDelete**
> oas_any_type_not_mapped deleteAssistantV1AssistantsAssistantIdDelete(assistant\_id)

Delete Assistant

    Delete assistant  API Reference docs - https://platform.openai.com/docs/api-reference/assistants/createAssistant

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **assistant\_id** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getAssistantsAssistantsGet"></a>
# **getAssistantsAssistantsGet**
> oas_any_type_not_mapped getAssistantsAssistantsGet()

Get Assistants

    Returns a list of assistants.  API Reference docs - https://platform.openai.com/docs/api-reference/assistants/listAssistants

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getAssistantsV1AssistantsGet"></a>
# **getAssistantsV1AssistantsGet**
> oas_any_type_not_mapped getAssistantsV1AssistantsGet()

Get Assistants

    Returns a list of assistants.  API Reference docs - https://platform.openai.com/docs/api-reference/assistants/listAssistants

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getMessagesThreadsThreadIdMessagesGet"></a>
# **getMessagesThreadsThreadIdMessagesGet**
> oas_any_type_not_mapped getMessagesThreadsThreadIdMessagesGet(thread\_id)

Get Messages

    Returns a list of messages for a given thread.  API Reference - https://platform.openai.com/docs/api-reference/messages/listMessages

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **thread\_id** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getMessagesV1ThreadsThreadIdMessagesGet"></a>
# **getMessagesV1ThreadsThreadIdMessagesGet**
> oas_any_type_not_mapped getMessagesV1ThreadsThreadIdMessagesGet(thread\_id)

Get Messages

    Returns a list of messages for a given thread.  API Reference - https://platform.openai.com/docs/api-reference/messages/listMessages

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **thread\_id** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getThreadThreadsThreadIdGet"></a>
# **getThreadThreadsThreadIdGet**
> oas_any_type_not_mapped getThreadThreadsThreadIdGet(thread\_id)

Get Thread

    Retrieves a thread.  API Reference - https://platform.openai.com/docs/api-reference/threads/getThread

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **thread\_id** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getThreadV1ThreadsThreadIdGet"></a>
# **getThreadV1ThreadsThreadIdGet**
> oas_any_type_not_mapped getThreadV1ThreadsThreadIdGet(thread\_id)

Get Thread

    Retrieves a thread.  API Reference - https://platform.openai.com/docs/api-reference/threads/getThread

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **thread\_id** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="runThreadThreadsThreadIdRunsPost"></a>
# **runThreadThreadsThreadIdRunsPost**
> oas_any_type_not_mapped runThreadThreadsThreadIdRunsPost(thread\_id)

Run Thread

    Create a run.  API Reference: https://platform.openai.com/docs/api-reference/runs/createRun

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **thread\_id** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="runThreadV1ThreadsThreadIdRunsPost"></a>
# **runThreadV1ThreadsThreadIdRunsPost**
> oas_any_type_not_mapped runThreadV1ThreadsThreadIdRunsPost(thread\_id)

Run Thread

    Create a run.  API Reference: https://platform.openai.com/docs/api-reference/runs/createRun

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **thread\_id** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

