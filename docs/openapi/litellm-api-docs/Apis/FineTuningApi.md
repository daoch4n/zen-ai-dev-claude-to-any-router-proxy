# FineTuningApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**cancelFineTuningJobFineTuningJobsFineTuningJobIdCancelPost**](FineTuningApi.md#cancelFineTuningJobFineTuningJobsFineTuningJobIdCancelPost) | **POST** /fine_tuning/jobs/{fine_tuning_job_id}/cancel | ✨ (Enterprise) Cancel Fine-Tuning Jobs |
| [**cancelFineTuningJobV1FineTuningJobsFineTuningJobIdCancelPost**](FineTuningApi.md#cancelFineTuningJobV1FineTuningJobsFineTuningJobIdCancelPost) | **POST** /v1/fine_tuning/jobs/{fine_tuning_job_id}/cancel | ✨ (Enterprise) Cancel Fine-Tuning Jobs |
| [**createFineTuningJobFineTuningJobsPost**](FineTuningApi.md#createFineTuningJobFineTuningJobsPost) | **POST** /fine_tuning/jobs | ✨ (Enterprise) Create Fine-Tuning Job |
| [**createFineTuningJobV1FineTuningJobsPost**](FineTuningApi.md#createFineTuningJobV1FineTuningJobsPost) | **POST** /v1/fine_tuning/jobs | ✨ (Enterprise) Create Fine-Tuning Job |
| [**listFineTuningJobsFineTuningJobsGet**](FineTuningApi.md#listFineTuningJobsFineTuningJobsGet) | **GET** /fine_tuning/jobs | ✨ (Enterprise) List Fine-Tuning Jobs |
| [**listFineTuningJobsV1FineTuningJobsGet**](FineTuningApi.md#listFineTuningJobsV1FineTuningJobsGet) | **GET** /v1/fine_tuning/jobs | ✨ (Enterprise) List Fine-Tuning Jobs |
| [**retrieveFineTuningJobFineTuningJobsFineTuningJobIdGet**](FineTuningApi.md#retrieveFineTuningJobFineTuningJobsFineTuningJobIdGet) | **GET** /fine_tuning/jobs/{fine_tuning_job_id} | ✨ (Enterprise) Retrieve Fine-Tuning Job |
| [**retrieveFineTuningJobV1FineTuningJobsFineTuningJobIdGet**](FineTuningApi.md#retrieveFineTuningJobV1FineTuningJobsFineTuningJobIdGet) | **GET** /v1/fine_tuning/jobs/{fine_tuning_job_id} | ✨ (Enterprise) Retrieve Fine-Tuning Job |


<a name="cancelFineTuningJobFineTuningJobsFineTuningJobIdCancelPost"></a>
# **cancelFineTuningJobFineTuningJobsFineTuningJobIdCancelPost**
> oas_any_type_not_mapped cancelFineTuningJobFineTuningJobsFineTuningJobIdCancelPost(fine\_tuning\_job\_id)

✨ (Enterprise) Cancel Fine-Tuning Jobs

    Cancel a fine-tuning job.  This is the equivalent of POST https://api.openai.com/v1/fine_tuning/jobs/{fine_tuning_job_id}/cancel  Supported Query Params: - &#x60;custom_llm_provider&#x60;: Name of the LiteLLM provider - &#x60;fine_tuning_job_id&#x60;: The ID of the fine-tuning job to cancel.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **fine\_tuning\_job\_id** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="cancelFineTuningJobV1FineTuningJobsFineTuningJobIdCancelPost"></a>
# **cancelFineTuningJobV1FineTuningJobsFineTuningJobIdCancelPost**
> oas_any_type_not_mapped cancelFineTuningJobV1FineTuningJobsFineTuningJobIdCancelPost(fine\_tuning\_job\_id)

✨ (Enterprise) Cancel Fine-Tuning Jobs

    Cancel a fine-tuning job.  This is the equivalent of POST https://api.openai.com/v1/fine_tuning/jobs/{fine_tuning_job_id}/cancel  Supported Query Params: - &#x60;custom_llm_provider&#x60;: Name of the LiteLLM provider - &#x60;fine_tuning_job_id&#x60;: The ID of the fine-tuning job to cancel.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **fine\_tuning\_job\_id** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="createFineTuningJobFineTuningJobsPost"></a>
# **createFineTuningJobFineTuningJobsPost**
> oas_any_type_not_mapped createFineTuningJobFineTuningJobsPost(LiteLLMFineTuningJobCreate)

✨ (Enterprise) Create Fine-Tuning Job

    Creates a fine-tuning job which begins the process of creating a new model from a given dataset. This is the equivalent of POST https://api.openai.com/v1/fine_tuning/jobs  Supports Identical Params as: https://platform.openai.com/docs/api-reference/fine-tuning/create  Example Curl: &#x60;&#x60;&#x60; curl http://localhost:4000/v1/fine_tuning/jobs       -H \&quot;Content-Type: application/json\&quot;       -H \&quot;Authorization: Bearer sk-1234\&quot;       -d &#39;{     \&quot;model\&quot;: \&quot;gpt-3.5-turbo\&quot;,     \&quot;training_file\&quot;: \&quot;file-abc123\&quot;,     \&quot;hyperparameters\&quot;: {       \&quot;n_epochs\&quot;: 4     }   }&#39; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **LiteLLMFineTuningJobCreate** | [**LiteLLMFineTuningJobCreate**](../Models/LiteLLMFineTuningJobCreate.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="createFineTuningJobV1FineTuningJobsPost"></a>
# **createFineTuningJobV1FineTuningJobsPost**
> oas_any_type_not_mapped createFineTuningJobV1FineTuningJobsPost(LiteLLMFineTuningJobCreate)

✨ (Enterprise) Create Fine-Tuning Job

    Creates a fine-tuning job which begins the process of creating a new model from a given dataset. This is the equivalent of POST https://api.openai.com/v1/fine_tuning/jobs  Supports Identical Params as: https://platform.openai.com/docs/api-reference/fine-tuning/create  Example Curl: &#x60;&#x60;&#x60; curl http://localhost:4000/v1/fine_tuning/jobs       -H \&quot;Content-Type: application/json\&quot;       -H \&quot;Authorization: Bearer sk-1234\&quot;       -d &#39;{     \&quot;model\&quot;: \&quot;gpt-3.5-turbo\&quot;,     \&quot;training_file\&quot;: \&quot;file-abc123\&quot;,     \&quot;hyperparameters\&quot;: {       \&quot;n_epochs\&quot;: 4     }   }&#39; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **LiteLLMFineTuningJobCreate** | [**LiteLLMFineTuningJobCreate**](../Models/LiteLLMFineTuningJobCreate.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="listFineTuningJobsFineTuningJobsGet"></a>
# **listFineTuningJobsFineTuningJobsGet**
> oas_any_type_not_mapped listFineTuningJobsFineTuningJobsGet(custom\_llm\_provider, target\_model\_names, after, limit)

✨ (Enterprise) List Fine-Tuning Jobs

    Lists fine-tuning jobs for the organization. This is the equivalent of GET https://api.openai.com/v1/fine_tuning/jobs  Supported Query Params: - &#x60;custom_llm_provider&#x60;: Name of the LiteLLM provider - &#x60;after&#x60;: Identifier for the last job from the previous pagination request. - &#x60;limit&#x60;: Number of fine-tuning jobs to retrieve (default is 20).

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **custom\_llm\_provider** | **String**|  | [optional] [default to null] [enum: openai, azure] |
| **target\_model\_names** | **String**| Comma separated list of model names to filter by. Example: &#39;gpt-4o,gpt-4o-mini&#39; | [optional] [default to null] |
| **after** | **String**|  | [optional] [default to null] |
| **limit** | **Integer**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="listFineTuningJobsV1FineTuningJobsGet"></a>
# **listFineTuningJobsV1FineTuningJobsGet**
> oas_any_type_not_mapped listFineTuningJobsV1FineTuningJobsGet(custom\_llm\_provider, target\_model\_names, after, limit)

✨ (Enterprise) List Fine-Tuning Jobs

    Lists fine-tuning jobs for the organization. This is the equivalent of GET https://api.openai.com/v1/fine_tuning/jobs  Supported Query Params: - &#x60;custom_llm_provider&#x60;: Name of the LiteLLM provider - &#x60;after&#x60;: Identifier for the last job from the previous pagination request. - &#x60;limit&#x60;: Number of fine-tuning jobs to retrieve (default is 20).

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **custom\_llm\_provider** | **String**|  | [optional] [default to null] [enum: openai, azure] |
| **target\_model\_names** | **String**| Comma separated list of model names to filter by. Example: &#39;gpt-4o,gpt-4o-mini&#39; | [optional] [default to null] |
| **after** | **String**|  | [optional] [default to null] |
| **limit** | **Integer**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="retrieveFineTuningJobFineTuningJobsFineTuningJobIdGet"></a>
# **retrieveFineTuningJobFineTuningJobsFineTuningJobIdGet**
> oas_any_type_not_mapped retrieveFineTuningJobFineTuningJobsFineTuningJobIdGet(fine\_tuning\_job\_id, custom\_llm\_provider)

✨ (Enterprise) Retrieve Fine-Tuning Job

    Retrieves a fine-tuning job. This is the equivalent of GET https://api.openai.com/v1/fine_tuning/jobs/{fine_tuning_job_id}  Supported Query Params: - &#x60;custom_llm_provider&#x60;: Name of the LiteLLM provider - &#x60;fine_tuning_job_id&#x60;: The ID of the fine-tuning job to retrieve.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **fine\_tuning\_job\_id** | **String**|  | [default to null] |
| **custom\_llm\_provider** | **String**|  | [optional] [default to null] [enum: openai, azure] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="retrieveFineTuningJobV1FineTuningJobsFineTuningJobIdGet"></a>
# **retrieveFineTuningJobV1FineTuningJobsFineTuningJobIdGet**
> oas_any_type_not_mapped retrieveFineTuningJobV1FineTuningJobsFineTuningJobIdGet(fine\_tuning\_job\_id, custom\_llm\_provider)

✨ (Enterprise) Retrieve Fine-Tuning Job

    Retrieves a fine-tuning job. This is the equivalent of GET https://api.openai.com/v1/fine_tuning/jobs/{fine_tuning_job_id}  Supported Query Params: - &#x60;custom_llm_provider&#x60;: Name of the LiteLLM provider - &#x60;fine_tuning_job_id&#x60;: The ID of the fine-tuning job to retrieve.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **fine\_tuning\_job\_id** | **String**|  | [default to null] |
| **custom\_llm\_provider** | **String**|  | [optional] [default to null] [enum: openai, azure] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

