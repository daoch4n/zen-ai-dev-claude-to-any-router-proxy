# GuardrailsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**applyGuardrailGuardrailsApplyGuardrailPost**](GuardrailsApi.md#applyGuardrailGuardrailsApplyGuardrailPost) | **POST** /guardrails/apply_guardrail | Apply Guardrail |
| [**createGuardrailGuardrailsPost**](GuardrailsApi.md#createGuardrailGuardrailsPost) | **POST** /guardrails | Create Guardrail |
| [**deleteGuardrailGuardrailsGuardrailIdDelete**](GuardrailsApi.md#deleteGuardrailGuardrailsGuardrailIdDelete) | **DELETE** /guardrails/{guardrail_id} | Delete Guardrail |
| [**getGuardrailGuardrailsGuardrailIdGet**](GuardrailsApi.md#getGuardrailGuardrailsGuardrailIdGet) | **GET** /guardrails/{guardrail_id} | Get Guardrail |
| [**getGuardrailInfoGuardrailsGuardrailIdInfoGet**](GuardrailsApi.md#getGuardrailInfoGuardrailsGuardrailIdInfoGet) | **GET** /guardrails/{guardrail_id}/info | Get Guardrail Info |
| [**getGuardrailUiSettingsGuardrailsUiAddGuardrailSettingsGet**](GuardrailsApi.md#getGuardrailUiSettingsGuardrailsUiAddGuardrailSettingsGet) | **GET** /guardrails/ui/add_guardrail_settings | Get Guardrail Ui Settings |
| [**getProviderSpecificParamsGuardrailsUiProviderSpecificParamsGet**](GuardrailsApi.md#getProviderSpecificParamsGuardrailsUiProviderSpecificParamsGet) | **GET** /guardrails/ui/provider_specific_params | Get Provider Specific Params |
| [**listGuardrailsGuardrailsListGet**](GuardrailsApi.md#listGuardrailsGuardrailsListGet) | **GET** /guardrails/list | List Guardrails |
| [**listGuardrailsV2V2GuardrailsListGet**](GuardrailsApi.md#listGuardrailsV2V2GuardrailsListGet) | **GET** /v2/guardrails/list | List Guardrails V2 |
| [**patchGuardrailGuardrailsGuardrailIdPatch**](GuardrailsApi.md#patchGuardrailGuardrailsGuardrailIdPatch) | **PATCH** /guardrails/{guardrail_id} | Patch Guardrail |
| [**updateGuardrailGuardrailsGuardrailIdPut**](GuardrailsApi.md#updateGuardrailGuardrailsGuardrailIdPut) | **PUT** /guardrails/{guardrail_id} | Update Guardrail |


<a name="applyGuardrailGuardrailsApplyGuardrailPost"></a>
# **applyGuardrailGuardrailsApplyGuardrailPost**
> ApplyGuardrailResponse applyGuardrailGuardrailsApplyGuardrailPost(ApplyGuardrailRequest)

Apply Guardrail

    Mask PII from a given text, requires a guardrail to be added to litellm.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **ApplyGuardrailRequest** | [**ApplyGuardrailRequest**](../Models/ApplyGuardrailRequest.md)|  | |

### Return type

[**ApplyGuardrailResponse**](../Models/ApplyGuardrailResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="createGuardrailGuardrailsPost"></a>
# **createGuardrailGuardrailsPost**
> oas_any_type_not_mapped createGuardrailGuardrailsPost(CreateGuardrailRequest)

Create Guardrail

    Create a new guardrail  👉 [Guardrail docs](https://docs.litellm.ai/docs/proxy/guardrails/quick_start)  Example Request: &#x60;&#x60;&#x60;bash curl -X POST \&quot;http://localhost:4000/guardrails\&quot; \\     -H \&quot;Authorization: Bearer &lt;your_api_key&gt;\&quot; \\     -H \&quot;Content-Type: application/json\&quot; \\     -d &#39;{         \&quot;guardrail\&quot;: {             \&quot;guardrail_name\&quot;: \&quot;my-bedrock-guard\&quot;,             \&quot;litellm_params\&quot;: {                 \&quot;guardrail\&quot;: \&quot;bedrock\&quot;,                 \&quot;mode\&quot;: \&quot;pre_call\&quot;,                 \&quot;guardrailIdentifier\&quot;: \&quot;ff6ujrregl1q\&quot;,                 \&quot;guardrailVersion\&quot;: \&quot;DRAFT\&quot;,                 \&quot;default_on\&quot;: true             },             \&quot;guardrail_info\&quot;: {                 \&quot;description\&quot;: \&quot;Bedrock content moderation guardrail\&quot;             }         }     }&#39; &#x60;&#x60;&#x60;  Example Response: &#x60;&#x60;&#x60;json {     \&quot;guardrail_id\&quot;: \&quot;123e4567-e89b-12d3-a456-426614174000\&quot;,     \&quot;guardrail_name\&quot;: \&quot;my-bedrock-guard\&quot;,     \&quot;litellm_params\&quot;: {         \&quot;guardrail\&quot;: \&quot;bedrock\&quot;,         \&quot;mode\&quot;: \&quot;pre_call\&quot;,         \&quot;guardrailIdentifier\&quot;: \&quot;ff6ujrregl1q\&quot;,         \&quot;guardrailVersion\&quot;: \&quot;DRAFT\&quot;,         \&quot;default_on\&quot;: true     },     \&quot;guardrail_info\&quot;: {         \&quot;description\&quot;: \&quot;Bedrock content moderation guardrail\&quot;     },     \&quot;created_at\&quot;: \&quot;2023-11-09T12:34:56.789Z\&quot;,     \&quot;updated_at\&quot;: \&quot;2023-11-09T12:34:56.789Z\&quot; } &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **CreateGuardrailRequest** | [**CreateGuardrailRequest**](../Models/CreateGuardrailRequest.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="deleteGuardrailGuardrailsGuardrailIdDelete"></a>
# **deleteGuardrailGuardrailsGuardrailIdDelete**
> oas_any_type_not_mapped deleteGuardrailGuardrailsGuardrailIdDelete(guardrail\_id)

Delete Guardrail

    Delete a guardrail  👉 [Guardrail docs](https://docs.litellm.ai/docs/proxy/guardrails/quick_start)  Example Request: &#x60;&#x60;&#x60;bash curl -X DELETE \&quot;http://localhost:4000/guardrails/123e4567-e89b-12d3-a456-426614174000\&quot; \\     -H \&quot;Authorization: Bearer &lt;your_api_key&gt;\&quot; &#x60;&#x60;&#x60;  Example Response: &#x60;&#x60;&#x60;json {     \&quot;message\&quot;: \&quot;Guardrail 123e4567-e89b-12d3-a456-426614174000 deleted successfully\&quot; } &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **guardrail\_id** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getGuardrailGuardrailsGuardrailIdGet"></a>
# **getGuardrailGuardrailsGuardrailIdGet**
> oas_any_type_not_mapped getGuardrailGuardrailsGuardrailIdGet(guardrail\_id)

Get Guardrail

    Get a guardrail by ID  👉 [Guardrail docs](https://docs.litellm.ai/docs/proxy/guardrails/quick_start)  Example Request: &#x60;&#x60;&#x60;bash curl -X GET \&quot;http://localhost:4000/guardrails/123e4567-e89b-12d3-a456-426614174000\&quot; \\     -H \&quot;Authorization: Bearer &lt;your_api_key&gt;\&quot; &#x60;&#x60;&#x60;  Example Response: &#x60;&#x60;&#x60;json {     \&quot;guardrail_id\&quot;: \&quot;123e4567-e89b-12d3-a456-426614174000\&quot;,     \&quot;guardrail_name\&quot;: \&quot;my-bedrock-guard\&quot;,     \&quot;litellm_params\&quot;: {         \&quot;guardrail\&quot;: \&quot;bedrock\&quot;,         \&quot;mode\&quot;: \&quot;pre_call\&quot;,         \&quot;guardrailIdentifier\&quot;: \&quot;ff6ujrregl1q\&quot;,         \&quot;guardrailVersion\&quot;: \&quot;DRAFT\&quot;,         \&quot;default_on\&quot;: true     },     \&quot;guardrail_info\&quot;: {         \&quot;description\&quot;: \&quot;Bedrock content moderation guardrail\&quot;     },     \&quot;created_at\&quot;: \&quot;2023-11-09T12:34:56.789Z\&quot;,     \&quot;updated_at\&quot;: \&quot;2023-11-09T12:34:56.789Z\&quot; } &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **guardrail\_id** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getGuardrailInfoGuardrailsGuardrailIdInfoGet"></a>
# **getGuardrailInfoGuardrailsGuardrailIdInfoGet**
> oas_any_type_not_mapped getGuardrailInfoGuardrailsGuardrailIdInfoGet(guardrail\_id)

Get Guardrail Info

    Get detailed information about a specific guardrail by ID  👉 [Guardrail docs](https://docs.litellm.ai/docs/proxy/guardrails/quick_start)  Example Request: &#x60;&#x60;&#x60;bash curl -X GET \&quot;http://localhost:4000/guardrails/123e4567-e89b-12d3-a456-426614174000/info\&quot; \\     -H \&quot;Authorization: Bearer &lt;your_api_key&gt;\&quot; &#x60;&#x60;&#x60;  Example Response: &#x60;&#x60;&#x60;json {     \&quot;guardrail_id\&quot;: \&quot;123e4567-e89b-12d3-a456-426614174000\&quot;,     \&quot;guardrail_name\&quot;: \&quot;my-bedrock-guard\&quot;,     \&quot;litellm_params\&quot;: {         \&quot;guardrail\&quot;: \&quot;bedrock\&quot;,         \&quot;mode\&quot;: \&quot;pre_call\&quot;,         \&quot;guardrailIdentifier\&quot;: \&quot;ff6ujrregl1q\&quot;,         \&quot;guardrailVersion\&quot;: \&quot;DRAFT\&quot;,         \&quot;default_on\&quot;: true     },     \&quot;guardrail_info\&quot;: {         \&quot;description\&quot;: \&quot;Bedrock content moderation guardrail\&quot;     },     \&quot;created_at\&quot;: \&quot;2023-11-09T12:34:56.789Z\&quot;,     \&quot;updated_at\&quot;: \&quot;2023-11-09T12:34:56.789Z\&quot; } &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **guardrail\_id** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getGuardrailUiSettingsGuardrailsUiAddGuardrailSettingsGet"></a>
# **getGuardrailUiSettingsGuardrailsUiAddGuardrailSettingsGet**
> oas_any_type_not_mapped getGuardrailUiSettingsGuardrailsUiAddGuardrailSettingsGet()

Get Guardrail Ui Settings

    Get the UI settings for the guardrails  Returns: - Supported entities for guardrails - Supported modes for guardrails - PII entity categories for UI organization

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getProviderSpecificParamsGuardrailsUiProviderSpecificParamsGet"></a>
# **getProviderSpecificParamsGuardrailsUiProviderSpecificParamsGet**
> oas_any_type_not_mapped getProviderSpecificParamsGuardrailsUiProviderSpecificParamsGet()

Get Provider Specific Params

    Get provider-specific parameters for different guardrail types.  Returns a dictionary mapping guardrail providers to their specific parameters, including parameter names, descriptions, and whether they are required.  Example Response: &#x60;&#x60;&#x60;json {     \&quot;bedrock\&quot;: [         {             \&quot;param\&quot;: \&quot;guardrailIdentifier\&quot;,             \&quot;description\&quot;: \&quot;The ID of your guardrail on Bedrock\&quot;,             \&quot;required\&quot;: true         },         {             \&quot;param\&quot;: \&quot;guardrailVersion\&quot;,             \&quot;description\&quot;: \&quot;The version of your Bedrock guardrail (e.g., DRAFT or version number)\&quot;,             \&quot;required\&quot;: true         }     ],     \&quot;presidio\&quot;: [         {             \&quot;param\&quot;: \&quot;presidio_analyzer_api_base\&quot;,             \&quot;description\&quot;: \&quot;Base URL for the Presidio analyzer API\&quot;,             \&quot;required\&quot;: true         },         {             \&quot;param\&quot;: \&quot;presidio_anonymizer_api_base\&quot;,             \&quot;description\&quot;: \&quot;Base URL for the Presidio anonymizer API\&quot;,             \&quot;required\&quot;: true         },         {             \&quot;param\&quot;: \&quot;output_parse_pii\&quot;,             \&quot;description\&quot;: \&quot;Whether to parse PII in model outputs\&quot;,             \&quot;required\&quot;: false,             \&quot;type\&quot;: \&quot;bool\&quot;         }     ] } &#x60;&#x60;&#x60;

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="listGuardrailsGuardrailsListGet"></a>
# **listGuardrailsGuardrailsListGet**
> ListGuardrailsResponse listGuardrailsGuardrailsListGet()

List Guardrails

    List the guardrails that are available on the proxy server  👉 [Guardrail docs](https://docs.litellm.ai/docs/proxy/guardrails/quick_start)  Example Request: &#x60;&#x60;&#x60;bash curl -X GET \&quot;http://localhost:4000/guardrails/list\&quot; -H \&quot;Authorization: Bearer &lt;your_api_key&gt;\&quot; &#x60;&#x60;&#x60;  Example Response: &#x60;&#x60;&#x60;json {     \&quot;guardrails\&quot;: [         {         \&quot;guardrail_name\&quot;: \&quot;bedrock-pre-guard\&quot;,         \&quot;guardrail_info\&quot;: {             \&quot;params\&quot;: [             {                 \&quot;name\&quot;: \&quot;toxicity_score\&quot;,                 \&quot;type\&quot;: \&quot;float\&quot;,                 \&quot;description\&quot;: \&quot;Score between 0-1 indicating content toxicity level\&quot;             },             {                 \&quot;name\&quot;: \&quot;pii_detection\&quot;,                 \&quot;type\&quot;: \&quot;boolean\&quot;             }             ]         }         }     ] } &#x60;&#x60;&#x60;

### Parameters
This endpoint does not need any parameter.

### Return type

[**ListGuardrailsResponse**](../Models/ListGuardrailsResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="listGuardrailsV2V2GuardrailsListGet"></a>
# **listGuardrailsV2V2GuardrailsListGet**
> ListGuardrailsResponse listGuardrailsV2V2GuardrailsListGet()

List Guardrails V2

    List the guardrails that are available in the database using GuardrailRegistry  👉 [Guardrail docs](https://docs.litellm.ai/docs/proxy/guardrails/quick_start)  Example Request: &#x60;&#x60;&#x60;bash curl -X GET \&quot;http://localhost:4000/v2/guardrails/list\&quot; -H \&quot;Authorization: Bearer &lt;your_api_key&gt;\&quot; &#x60;&#x60;&#x60;  Example Response: &#x60;&#x60;&#x60;json {     \&quot;guardrails\&quot;: [         {             \&quot;guardrail_id\&quot;: \&quot;123e4567-e89b-12d3-a456-426614174000\&quot;,             \&quot;guardrail_name\&quot;: \&quot;my-bedrock-guard\&quot;,             \&quot;litellm_params\&quot;: {                 \&quot;guardrail\&quot;: \&quot;bedrock\&quot;,                 \&quot;mode\&quot;: \&quot;pre_call\&quot;,                 \&quot;guardrailIdentifier\&quot;: \&quot;ff6ujrregl1q\&quot;,                 \&quot;guardrailVersion\&quot;: \&quot;DRAFT\&quot;,                 \&quot;default_on\&quot;: true             },             \&quot;guardrail_info\&quot;: {                 \&quot;description\&quot;: \&quot;Bedrock content moderation guardrail\&quot;             }         }     ] } &#x60;&#x60;&#x60;

### Parameters
This endpoint does not need any parameter.

### Return type

[**ListGuardrailsResponse**](../Models/ListGuardrailsResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="patchGuardrailGuardrailsGuardrailIdPatch"></a>
# **patchGuardrailGuardrailsGuardrailIdPatch**
> oas_any_type_not_mapped patchGuardrailGuardrailsGuardrailIdPatch(guardrail\_id, PatchGuardrailRequest)

Patch Guardrail

    Partially update an existing guardrail  👉 [Guardrail docs](https://docs.litellm.ai/docs/proxy/guardrails/quick_start)  This endpoint allows updating specific fields of a guardrail without sending the entire object. Only the following fields can be updated: - guardrail_name: The name of the guardrail - default_on: Whether the guardrail is enabled by default - guardrail_info: Additional information about the guardrail  Example Request: &#x60;&#x60;&#x60;bash curl -X PATCH \&quot;http://localhost:4000/guardrails/123e4567-e89b-12d3-a456-426614174000\&quot; \\     -H \&quot;Authorization: Bearer &lt;your_api_key&gt;\&quot; \\     -H \&quot;Content-Type: application/json\&quot; \\     -d &#39;{         \&quot;guardrail_name\&quot;: \&quot;updated-name\&quot;,         \&quot;default_on\&quot;: true,         \&quot;guardrail_info\&quot;: {             \&quot;description\&quot;: \&quot;Updated description\&quot;         }     }&#39; &#x60;&#x60;&#x60;  Example Response: &#x60;&#x60;&#x60;json {     \&quot;guardrail_id\&quot;: \&quot;123e4567-e89b-12d3-a456-426614174000\&quot;,     \&quot;guardrail_name\&quot;: \&quot;updated-name\&quot;,     \&quot;litellm_params\&quot;: {         \&quot;guardrail\&quot;: \&quot;bedrock\&quot;,         \&quot;mode\&quot;: \&quot;pre_call\&quot;,         \&quot;guardrailIdentifier\&quot;: \&quot;ff6ujrregl1q\&quot;,         \&quot;guardrailVersion\&quot;: \&quot;DRAFT\&quot;,         \&quot;default_on\&quot;: true     },     \&quot;guardrail_info\&quot;: {         \&quot;description\&quot;: \&quot;Updated description\&quot;     },     \&quot;created_at\&quot;: \&quot;2023-11-09T12:34:56.789Z\&quot;,     \&quot;updated_at\&quot;: \&quot;2023-11-09T14:22:33.456Z\&quot; } &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **guardrail\_id** | **String**|  | [default to null] |
| **PatchGuardrailRequest** | [**PatchGuardrailRequest**](../Models/PatchGuardrailRequest.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="updateGuardrailGuardrailsGuardrailIdPut"></a>
# **updateGuardrailGuardrailsGuardrailIdPut**
> oas_any_type_not_mapped updateGuardrailGuardrailsGuardrailIdPut(guardrail\_id, UpdateGuardrailRequest)

Update Guardrail

    Update an existing guardrail  👉 [Guardrail docs](https://docs.litellm.ai/docs/proxy/guardrails/quick_start)  Example Request: &#x60;&#x60;&#x60;bash curl -X PUT \&quot;http://localhost:4000/guardrails/123e4567-e89b-12d3-a456-426614174000\&quot; \\     -H \&quot;Authorization: Bearer &lt;your_api_key&gt;\&quot; \\     -H \&quot;Content-Type: application/json\&quot; \\     -d &#39;{         \&quot;guardrail\&quot;: {             \&quot;guardrail_name\&quot;: \&quot;updated-bedrock-guard\&quot;,             \&quot;litellm_params\&quot;: {                 \&quot;guardrail\&quot;: \&quot;bedrock\&quot;,                 \&quot;mode\&quot;: \&quot;pre_call\&quot;,                 \&quot;guardrailIdentifier\&quot;: \&quot;ff6ujrregl1q\&quot;,                 \&quot;guardrailVersion\&quot;: \&quot;1.0\&quot;,                 \&quot;default_on\&quot;: true             },             \&quot;guardrail_info\&quot;: {                 \&quot;description\&quot;: \&quot;Updated Bedrock content moderation guardrail\&quot;             }         }     }&#39; &#x60;&#x60;&#x60;  Example Response: &#x60;&#x60;&#x60;json {     \&quot;guardrail_id\&quot;: \&quot;123e4567-e89b-12d3-a456-426614174000\&quot;,     \&quot;guardrail_name\&quot;: \&quot;updated-bedrock-guard\&quot;,     \&quot;litellm_params\&quot;: {         \&quot;guardrail\&quot;: \&quot;bedrock\&quot;,         \&quot;mode\&quot;: \&quot;pre_call\&quot;,         \&quot;guardrailIdentifier\&quot;: \&quot;ff6ujrregl1q\&quot;,         \&quot;guardrailVersion\&quot;: \&quot;1.0\&quot;,         \&quot;default_on\&quot;: true     },     \&quot;guardrail_info\&quot;: {         \&quot;description\&quot;: \&quot;Updated Bedrock content moderation guardrail\&quot;     },     \&quot;created_at\&quot;: \&quot;2023-11-09T12:34:56.789Z\&quot;,     \&quot;updated_at\&quot;: \&quot;2023-11-09T13:45:12.345Z\&quot; } &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **guardrail\_id** | **String**|  | [default to null] |
| **UpdateGuardrailRequest** | [**UpdateGuardrailRequest**](../Models/UpdateGuardrailRequest.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

