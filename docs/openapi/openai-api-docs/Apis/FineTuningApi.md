# FineTuningApi

All URIs are relative to *https://api.openai.com/v1*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**cancelFineTuningJob**](FineTuningApi.md#cancelFineTuningJob) | **POST** /fine_tuning/jobs/{fine_tuning_job_id}/cancel | Immediately cancel a fine-tune job.  |
| [**createFineTuningCheckpointPermission**](FineTuningApi.md#createFineTuningCheckpointPermission) | **POST** /fine_tuning/checkpoints/{fine_tuned_model_checkpoint}/permissions | **NOTE:** Calling this endpoint requires an [admin API key](../admin-api-keys).  This enables organization owners to share fine-tuned models with other projects in their organization.  |
| [**createFineTuningJob**](FineTuningApi.md#createFineTuningJob) | **POST** /fine_tuning/jobs | Creates a fine-tuning job which begins the process of creating a new model from a given dataset.  Response includes details of the enqueued job including job status and the name of the fine-tuned models once complete.  [Learn more about fine-tuning](/docs/guides/fine-tuning)  |
| [**deleteFineTuningCheckpointPermission**](FineTuningApi.md#deleteFineTuningCheckpointPermission) | **DELETE** /fine_tuning/checkpoints/{fine_tuned_model_checkpoint}/permissions/{permission_id} | **NOTE:** This endpoint requires an [admin API key](../admin-api-keys).  Organization owners can use this endpoint to delete a permission for a fine-tuned model checkpoint.  |
| [**listFineTuningCheckpointPermissions**](FineTuningApi.md#listFineTuningCheckpointPermissions) | **GET** /fine_tuning/checkpoints/{fine_tuned_model_checkpoint}/permissions | **NOTE:** This endpoint requires an [admin API key](../admin-api-keys).  Organization owners can use this endpoint to view all permissions for a fine-tuned model checkpoint.  |
| [**listFineTuningEvents**](FineTuningApi.md#listFineTuningEvents) | **GET** /fine_tuning/jobs/{fine_tuning_job_id}/events | Get status updates for a fine-tuning job.  |
| [**listFineTuningJobCheckpoints**](FineTuningApi.md#listFineTuningJobCheckpoints) | **GET** /fine_tuning/jobs/{fine_tuning_job_id}/checkpoints | List checkpoints for a fine-tuning job.  |
| [**listPaginatedFineTuningJobs**](FineTuningApi.md#listPaginatedFineTuningJobs) | **GET** /fine_tuning/jobs | List your organization&#39;s fine-tuning jobs  |
| [**retrieveFineTuningJob**](FineTuningApi.md#retrieveFineTuningJob) | **GET** /fine_tuning/jobs/{fine_tuning_job_id} | Get info about a fine-tuning job.  [Learn more about fine-tuning](/docs/guides/fine-tuning)  |


<a name="cancelFineTuningJob"></a>
# **cancelFineTuningJob**
> FineTuningJob cancelFineTuningJob(fine\_tuning\_job\_id)

Immediately cancel a fine-tune job. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **fine\_tuning\_job\_id** | **String**| The ID of the fine-tuning job to cancel.  | [default to null] |

### Return type

[**FineTuningJob**](../Models/FineTuningJob.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="createFineTuningCheckpointPermission"></a>
# **createFineTuningCheckpointPermission**
> ListFineTuningCheckpointPermissionResponse createFineTuningCheckpointPermission(fine\_tuned\_model\_checkpoint, CreateFineTuningCheckpointPermissionRequest)

**NOTE:** Calling this endpoint requires an [admin API key](../admin-api-keys).  This enables organization owners to share fine-tuned models with other projects in their organization. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **fine\_tuned\_model\_checkpoint** | **String**| The ID of the fine-tuned model checkpoint to create a permission for.  | [default to null] |
| **CreateFineTuningCheckpointPermissionRequest** | [**CreateFineTuningCheckpointPermissionRequest**](../Models/CreateFineTuningCheckpointPermissionRequest.md)|  | |

### Return type

[**ListFineTuningCheckpointPermissionResponse**](../Models/ListFineTuningCheckpointPermissionResponse.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="createFineTuningJob"></a>
# **createFineTuningJob**
> FineTuningJob createFineTuningJob(CreateFineTuningJobRequest)

Creates a fine-tuning job which begins the process of creating a new model from a given dataset.  Response includes details of the enqueued job including job status and the name of the fine-tuned models once complete.  [Learn more about fine-tuning](/docs/guides/fine-tuning) 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **CreateFineTuningJobRequest** | [**CreateFineTuningJobRequest**](../Models/CreateFineTuningJobRequest.md)|  | |

### Return type

[**FineTuningJob**](../Models/FineTuningJob.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="deleteFineTuningCheckpointPermission"></a>
# **deleteFineTuningCheckpointPermission**
> DeleteFineTuningCheckpointPermissionResponse deleteFineTuningCheckpointPermission(fine\_tuned\_model\_checkpoint, permission\_id)

**NOTE:** This endpoint requires an [admin API key](../admin-api-keys).  Organization owners can use this endpoint to delete a permission for a fine-tuned model checkpoint. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **fine\_tuned\_model\_checkpoint** | **String**| The ID of the fine-tuned model checkpoint to delete a permission for.  | [default to null] |
| **permission\_id** | **String**| The ID of the fine-tuned model checkpoint permission to delete.  | [default to null] |

### Return type

[**DeleteFineTuningCheckpointPermissionResponse**](../Models/DeleteFineTuningCheckpointPermissionResponse.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="listFineTuningCheckpointPermissions"></a>
# **listFineTuningCheckpointPermissions**
> ListFineTuningCheckpointPermissionResponse listFineTuningCheckpointPermissions(fine\_tuned\_model\_checkpoint, project\_id, after, limit, order)

**NOTE:** This endpoint requires an [admin API key](../admin-api-keys).  Organization owners can use this endpoint to view all permissions for a fine-tuned model checkpoint. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **fine\_tuned\_model\_checkpoint** | **String**| The ID of the fine-tuned model checkpoint to get permissions for.  | [default to null] |
| **project\_id** | **String**| The ID of the project to get permissions for. | [optional] [default to null] |
| **after** | **String**| Identifier for the last permission ID from the previous pagination request. | [optional] [default to null] |
| **limit** | **Integer**| Number of permissions to retrieve. | [optional] [default to 10] |
| **order** | **String**| The order in which to retrieve permissions. | [optional] [default to descending] [enum: ascending, descending] |

### Return type

[**ListFineTuningCheckpointPermissionResponse**](../Models/ListFineTuningCheckpointPermissionResponse.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="listFineTuningEvents"></a>
# **listFineTuningEvents**
> ListFineTuningJobEventsResponse listFineTuningEvents(fine\_tuning\_job\_id, after, limit)

Get status updates for a fine-tuning job. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **fine\_tuning\_job\_id** | **String**| The ID of the fine-tuning job to get events for.  | [default to null] |
| **after** | **String**| Identifier for the last event from the previous pagination request. | [optional] [default to null] |
| **limit** | **Integer**| Number of events to retrieve. | [optional] [default to 20] |

### Return type

[**ListFineTuningJobEventsResponse**](../Models/ListFineTuningJobEventsResponse.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="listFineTuningJobCheckpoints"></a>
# **listFineTuningJobCheckpoints**
> ListFineTuningJobCheckpointsResponse listFineTuningJobCheckpoints(fine\_tuning\_job\_id, after, limit)

List checkpoints for a fine-tuning job. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **fine\_tuning\_job\_id** | **String**| The ID of the fine-tuning job to get checkpoints for.  | [default to null] |
| **after** | **String**| Identifier for the last checkpoint ID from the previous pagination request. | [optional] [default to null] |
| **limit** | **Integer**| Number of checkpoints to retrieve. | [optional] [default to 10] |

### Return type

[**ListFineTuningJobCheckpointsResponse**](../Models/ListFineTuningJobCheckpointsResponse.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="listPaginatedFineTuningJobs"></a>
# **listPaginatedFineTuningJobs**
> ListPaginatedFineTuningJobsResponse listPaginatedFineTuningJobs(after, limit, metadata)

List your organization&#39;s fine-tuning jobs 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **after** | **String**| Identifier for the last job from the previous pagination request. | [optional] [default to null] |
| **limit** | **Integer**| Number of fine-tuning jobs to retrieve. | [optional] [default to 20] |
| **metadata** | [**Map**](../Models/String.md)| Optional metadata filter. To filter, use the syntax &#x60;metadata[k]&#x3D;v&#x60;. Alternatively, set &#x60;metadata&#x3D;null&#x60; to indicate no metadata.  | [optional] [default to null] |

### Return type

[**ListPaginatedFineTuningJobsResponse**](../Models/ListPaginatedFineTuningJobsResponse.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="retrieveFineTuningJob"></a>
# **retrieveFineTuningJob**
> FineTuningJob retrieveFineTuningJob(fine\_tuning\_job\_id)

Get info about a fine-tuning job.  [Learn more about fine-tuning](/docs/guides/fine-tuning) 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **fine\_tuning\_job\_id** | **String**| The ID of the fine-tuning job.  | [default to null] |

### Return type

[**FineTuningJob**](../Models/FineTuningJob.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

