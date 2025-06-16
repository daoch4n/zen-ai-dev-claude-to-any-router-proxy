# ModelManagementApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**addNewModelModelNewPost**](ModelManagementApi.md#addNewModelModelNewPost) | **POST** /model/new | Add New Model |
| [**deleteModelModelDeletePost**](ModelManagementApi.md#deleteModelModelDeletePost) | **POST** /model/delete | Delete Model |
| [**modelGroupInfoModelGroupInfoGet**](ModelManagementApi.md#modelGroupInfoModelGroupInfoGet) | **GET** /model_group/info | Model Group Info |
| [**modelInfoV1ModelInfoGet**](ModelManagementApi.md#modelInfoV1ModelInfoGet) | **GET** /model/info | Model Info V1 |
| [**modelInfoV1V1ModelInfoGet**](ModelManagementApi.md#modelInfoV1V1ModelInfoGet) | **GET** /v1/model/info | Model Info V1 |
| [**modelListModelsGet**](ModelManagementApi.md#modelListModelsGet) | **GET** /models | Model List |
| [**modelListV1ModelsGet**](ModelManagementApi.md#modelListV1ModelsGet) | **GET** /v1/models | Model List |
| [**patchModelModelModelIdUpdatePatch**](ModelManagementApi.md#patchModelModelModelIdUpdatePatch) | **PATCH** /model/{model_id}/update | Patch Model |
| [**updateModelModelUpdatePost**](ModelManagementApi.md#updateModelModelUpdatePost) | **POST** /model/update | Update Model |


<a name="addNewModelModelNewPost"></a>
# **addNewModelModelNewPost**
> oas_any_type_not_mapped addNewModelModelNewPost(Deployment)

Add New Model

    Allows adding new models to the model list in the config.yaml

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **Deployment** | [**Deployment**](../Models/Deployment.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="deleteModelModelDeletePost"></a>
# **deleteModelModelDeletePost**
> oas_any_type_not_mapped deleteModelModelDeletePost(ModelInfoDelete)

Delete Model

    Allows deleting models in the model list in the config.yaml

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **ModelInfoDelete** | [**ModelInfoDelete**](../Models/ModelInfoDelete.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="modelGroupInfoModelGroupInfoGet"></a>
# **modelGroupInfoModelGroupInfoGet**
> oas_any_type_not_mapped modelGroupInfoModelGroupInfoGet(model\_group)

Model Group Info

    Get information about all the deployments on litellm proxy, including config.yaml descriptions (except api key and api base)  - /model_group/info returns all model groups. End users of proxy should use /model_group/info since those models will be used for /chat/completions, /embeddings, etc. - /model_group/info?model_group&#x3D;rerank-english-v3.0 returns all model groups for a specific model group (&#x60;model_name&#x60; in config.yaml)    Example Request (All Models): &#x60;&#x60;&#x60;shell curl -X &#39;GET&#39;     &#39;http://localhost:4000/model_group/info&#39;     -H &#39;accept: application/json&#39;     -H &#39;x-api-key: sk-1234&#39; &#x60;&#x60;&#x60;  Example Request (Specific Model Group): &#x60;&#x60;&#x60;shell curl -X &#39;GET&#39;     &#39;http://localhost:4000/model_group/info?model_group&#x3D;rerank-english-v3.0&#39;     -H &#39;accept: application/json&#39;     -H &#39;Authorization: Bearer sk-1234&#39; &#x60;&#x60;&#x60;  Example Request (Specific Wildcard Model Group): (e.g. &#x60;model_name: openai/*&#x60; on config.yaml) &#x60;&#x60;&#x60;shell curl -X &#39;GET&#39;     &#39;http://localhost:4000/model_group/info?model_group&#x3D;openai/tts-1&#39; -H &#39;accept: application/json&#39;     -H &#39;Authorization: Bearersk-1234&#39; &#x60;&#x60;&#x60;  Learn how to use and set wildcard models [here](https://docs.litellm.ai/docs/wildcard_routing)  Example Response: &#x60;&#x60;&#x60;json     {         \&quot;data\&quot;: [             {             \&quot;model_group\&quot;: \&quot;rerank-english-v3.0\&quot;,             \&quot;providers\&quot;: [                 \&quot;cohere\&quot;             ],             \&quot;max_input_tokens\&quot;: null,             \&quot;max_output_tokens\&quot;: null,             \&quot;input_cost_per_token\&quot;: 0.0,             \&quot;output_cost_per_token\&quot;: 0.0,             \&quot;mode\&quot;: null,             \&quot;tpm\&quot;: null,             \&quot;rpm\&quot;: null,             \&quot;supports_parallel_function_calling\&quot;: false,             \&quot;supports_vision\&quot;: false,             \&quot;supports_function_calling\&quot;: false,             \&quot;supported_openai_params\&quot;: [                 \&quot;stream\&quot;,                 \&quot;temperature\&quot;,                 \&quot;max_tokens\&quot;,                 \&quot;logit_bias\&quot;,                 \&quot;top_p\&quot;,                 \&quot;frequency_penalty\&quot;,                 \&quot;presence_penalty\&quot;,                 \&quot;stop\&quot;,                 \&quot;n\&quot;,                 \&quot;extra_headers\&quot;             ]             },             {             \&quot;model_group\&quot;: \&quot;gpt-3.5-turbo\&quot;,             \&quot;providers\&quot;: [                 \&quot;openai\&quot;             ],             \&quot;max_input_tokens\&quot;: 16385.0,             \&quot;max_output_tokens\&quot;: 4096.0,             \&quot;input_cost_per_token\&quot;: 1.5e-06,             \&quot;output_cost_per_token\&quot;: 2e-06,             \&quot;mode\&quot;: \&quot;chat\&quot;,             \&quot;tpm\&quot;: null,             \&quot;rpm\&quot;: null,             \&quot;supports_parallel_function_calling\&quot;: false,             \&quot;supports_vision\&quot;: false,             \&quot;supports_function_calling\&quot;: true,             \&quot;supported_openai_params\&quot;: [                 \&quot;frequency_penalty\&quot;,                 \&quot;logit_bias\&quot;,                 \&quot;logprobs\&quot;,                 \&quot;top_logprobs\&quot;,                 \&quot;max_tokens\&quot;,                 \&quot;max_completion_tokens\&quot;,                 \&quot;n\&quot;,                 \&quot;presence_penalty\&quot;,                 \&quot;seed\&quot;,                 \&quot;stop\&quot;,                 \&quot;stream\&quot;,                 \&quot;stream_options\&quot;,                 \&quot;temperature\&quot;,                 \&quot;top_p\&quot;,                 \&quot;tools\&quot;,                 \&quot;tool_choice\&quot;,                 \&quot;function_call\&quot;,                 \&quot;functions\&quot;,                 \&quot;max_retries\&quot;,                 \&quot;extra_headers\&quot;,                 \&quot;parallel_tool_calls\&quot;,                 \&quot;response_format\&quot;             ]             },             {             \&quot;model_group\&quot;: \&quot;llava-hf\&quot;,             \&quot;providers\&quot;: [                 \&quot;openai\&quot;             ],             \&quot;max_input_tokens\&quot;: null,             \&quot;max_output_tokens\&quot;: null,             \&quot;input_cost_per_token\&quot;: 0.0,             \&quot;output_cost_per_token\&quot;: 0.0,             \&quot;mode\&quot;: null,             \&quot;tpm\&quot;: null,             \&quot;rpm\&quot;: null,             \&quot;supports_parallel_function_calling\&quot;: false,             \&quot;supports_vision\&quot;: true,             \&quot;supports_function_calling\&quot;: false,             \&quot;supported_openai_params\&quot;: [                 \&quot;frequency_penalty\&quot;,                 \&quot;logit_bias\&quot;,                 \&quot;logprobs\&quot;,                 \&quot;top_logprobs\&quot;,                 \&quot;max_tokens\&quot;,                 \&quot;max_completion_tokens\&quot;,                 \&quot;n\&quot;,                 \&quot;presence_penalty\&quot;,                 \&quot;seed\&quot;,                 \&quot;stop\&quot;,                 \&quot;stream\&quot;,                 \&quot;stream_options\&quot;,                 \&quot;temperature\&quot;,                 \&quot;top_p\&quot;,                 \&quot;tools\&quot;,                 \&quot;tool_choice\&quot;,                 \&quot;function_call\&quot;,                 \&quot;functions\&quot;,                 \&quot;max_retries\&quot;,                 \&quot;extra_headers\&quot;,                 \&quot;parallel_tool_calls\&quot;,                 \&quot;response_format\&quot;             ]             }         ]         } &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **model\_group** | **String**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="modelInfoV1ModelInfoGet"></a>
# **modelInfoV1ModelInfoGet**
> oas_any_type_not_mapped modelInfoV1ModelInfoGet(litellm\_model\_id)

Model Info V1

    Provides more info about each model in /models, including config.yaml descriptions (except api key and api base)  Parameters:     litellm_model_id: Optional[str] &#x3D; None (this is the value of &#x60;x-litellm-model-id&#x60; returned in response headers)      - When litellm_model_id is passed, it will return the info for that specific model     - When litellm_model_id is not passed, it will return the info for all models  Returns:     Returns a dictionary containing information about each model.  Example Response: &#x60;&#x60;&#x60;json {     \&quot;data\&quot;: [                 {                     \&quot;model_name\&quot;: \&quot;fake-openai-endpoint\&quot;,                     \&quot;litellm_params\&quot;: {                         \&quot;api_base\&quot;: \&quot;https://exampleopenaiendpoint-production.up.railway.app/\&quot;,                         \&quot;model\&quot;: \&quot;openai/fake\&quot;                     },                     \&quot;model_info\&quot;: {                         \&quot;id\&quot;: \&quot;112f74fab24a7a5245d2ced3536dd8f5f9192c57ee6e332af0f0512e08bed5af\&quot;,                         \&quot;db_model\&quot;: false                     }                 }             ] }  &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **litellm\_model\_id** | **String**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="modelInfoV1V1ModelInfoGet"></a>
# **modelInfoV1V1ModelInfoGet**
> oas_any_type_not_mapped modelInfoV1V1ModelInfoGet(litellm\_model\_id)

Model Info V1

    Provides more info about each model in /models, including config.yaml descriptions (except api key and api base)  Parameters:     litellm_model_id: Optional[str] &#x3D; None (this is the value of &#x60;x-litellm-model-id&#x60; returned in response headers)      - When litellm_model_id is passed, it will return the info for that specific model     - When litellm_model_id is not passed, it will return the info for all models  Returns:     Returns a dictionary containing information about each model.  Example Response: &#x60;&#x60;&#x60;json {     \&quot;data\&quot;: [                 {                     \&quot;model_name\&quot;: \&quot;fake-openai-endpoint\&quot;,                     \&quot;litellm_params\&quot;: {                         \&quot;api_base\&quot;: \&quot;https://exampleopenaiendpoint-production.up.railway.app/\&quot;,                         \&quot;model\&quot;: \&quot;openai/fake\&quot;                     },                     \&quot;model_info\&quot;: {                         \&quot;id\&quot;: \&quot;112f74fab24a7a5245d2ced3536dd8f5f9192c57ee6e332af0f0512e08bed5af\&quot;,                         \&quot;db_model\&quot;: false                     }                 }             ] }  &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **litellm\_model\_id** | **String**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="modelListModelsGet"></a>
# **modelListModelsGet**
> oas_any_type_not_mapped modelListModelsGet(return\_wildcard\_routes, team\_id, include\_model\_access\_groups)

Model List

    Use &#x60;/model/info&#x60; - to get detailed model information, example - pricing, mode, etc.  This is just for compatibility with openai projects like aider.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **return\_wildcard\_routes** | **Boolean**|  | [optional] [default to null] |
| **team\_id** | **String**|  | [optional] [default to null] |
| **include\_model\_access\_groups** | **Boolean**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="modelListV1ModelsGet"></a>
# **modelListV1ModelsGet**
> oas_any_type_not_mapped modelListV1ModelsGet(return\_wildcard\_routes, team\_id, include\_model\_access\_groups)

Model List

    Use &#x60;/model/info&#x60; - to get detailed model information, example - pricing, mode, etc.  This is just for compatibility with openai projects like aider.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **return\_wildcard\_routes** | **Boolean**|  | [optional] [default to null] |
| **team\_id** | **String**|  | [optional] [default to null] |
| **include\_model\_access\_groups** | **Boolean**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="patchModelModelModelIdUpdatePatch"></a>
# **patchModelModelModelIdUpdatePatch**
> oas_any_type_not_mapped patchModelModelModelIdUpdatePatch(model\_id, updateDeployment)

Patch Model

    PATCH Endpoint for partial model updates.  Only updates the fields specified in the request while preserving other existing values. Follows proper PATCH semantics by only modifying provided fields.  Args:     model_id: The ID of the model to update     patch_data: The fields to update and their new values     user_api_key_dict: User authentication information  Returns:     Updated model information  Raises:     ProxyException: For various error conditions including authentication and database errors

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **model\_id** | **String**|  | [default to null] |
| **updateDeployment** | [**updateDeployment**](../Models/updateDeployment.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="updateModelModelUpdatePost"></a>
# **updateModelModelUpdatePost**
> oas_any_type_not_mapped updateModelModelUpdatePost(updateDeployment)

Update Model

    Edit existing model params

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **updateDeployment** | [**updateDeployment**](../Models/updateDeployment.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

