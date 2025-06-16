# BudgetSpendTrackingApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**addAllowedIpAddAllowedIpPost**](BudgetSpendTrackingApi.md#addAllowedIpAddAllowedIpPost) | **POST** /add/allowed_ip | Add Allowed Ip |
| [**calculateSpendSpendCalculatePost**](BudgetSpendTrackingApi.md#calculateSpendSpendCalculatePost) | **POST** /spend/calculate | Calculate Spend |
| [**deleteAllowedIpDeleteAllowedIpPost**](BudgetSpendTrackingApi.md#deleteAllowedIpDeleteAllowedIpPost) | **POST** /delete/allowed_ip | Delete Allowed Ip |
| [**getGlobalSpendReportGlobalSpendReportGet**](BudgetSpendTrackingApi.md#getGlobalSpendReportGlobalSpendReportGet) | **GET** /global/spend/report | Get Global Spend Report |
| [**getUserDailyActivityUserDailyActivityGet**](BudgetSpendTrackingApi.md#getUserDailyActivityUserDailyActivityGet) | **GET** /user/daily/activity | Get User Daily Activity |
| [**globalSpendResetGlobalSpendResetPost**](BudgetSpendTrackingApi.md#globalSpendResetGlobalSpendResetPost) | **POST** /global/spend/reset | Global Spend Reset |
| [**globalViewSpendTagsGlobalSpendTagsGet**](BudgetSpendTrackingApi.md#globalViewSpendTagsGlobalSpendTagsGet) | **GET** /global/spend/tags | Global View Spend Tags |
| [**viewSpendLogsSpendLogsGet**](BudgetSpendTrackingApi.md#viewSpendLogsSpendLogsGet) | **GET** /spend/logs | View Spend Logs |
| [**viewSpendTagsSpendTagsGet**](BudgetSpendTrackingApi.md#viewSpendTagsSpendTagsGet) | **GET** /spend/tags | View Spend Tags |


<a name="addAllowedIpAddAllowedIpPost"></a>
# **addAllowedIpAddAllowedIpPost**
> oas_any_type_not_mapped addAllowedIpAddAllowedIpPost(IPAddress)

Add Allowed Ip

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **IPAddress** | [**IPAddress**](../Models/IPAddress.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="calculateSpendSpendCalculatePost"></a>
# **calculateSpendSpendCalculatePost**
> oas_any_type_not_mapped calculateSpendSpendCalculatePost(SpendCalculateRequest)

Calculate Spend

    Accepts all the params of completion_cost.  Calculate spend **before** making call:  Note: If you see a spend of $0.0 you need to set custom_pricing for your model: https://docs.litellm.ai/docs/proxy/custom_pricing  &#x60;&#x60;&#x60; curl --location &#39;http://localhost:4000/spend/calculate&#39; --header &#39;Authorization: Bearer sk-1234&#39; --header &#39;Content-Type: application/json&#39; --data &#39;{     \&quot;model\&quot;: \&quot;anthropic.claude-v2\&quot;,     \&quot;messages\&quot;: [{\&quot;role\&quot;: \&quot;user\&quot;, \&quot;content\&quot;: \&quot;Hey, how&#39;&#39;&#39;s it going?\&quot;}] }&#39; &#x60;&#x60;&#x60;  Calculate spend **after** making call:  &#x60;&#x60;&#x60; curl --location &#39;http://localhost:4000/spend/calculate&#39; --header &#39;Authorization: Bearer sk-1234&#39; --header &#39;Content-Type: application/json&#39; --data &#39;{     \&quot;completion_response\&quot;: {         \&quot;id\&quot;: \&quot;chatcmpl-123\&quot;,         \&quot;object\&quot;: \&quot;chat.completion\&quot;,         \&quot;created\&quot;: 1677652288,         \&quot;model\&quot;: \&quot;gpt-3.5-turbo-0125\&quot;,         \&quot;system_fingerprint\&quot;: \&quot;fp_44709d6fcb\&quot;,         \&quot;choices\&quot;: [{             \&quot;index\&quot;: 0,             \&quot;message\&quot;: {                 \&quot;role\&quot;: \&quot;assistant\&quot;,                 \&quot;content\&quot;: \&quot;Hello there, how may I assist you today?\&quot;             },             \&quot;logprobs\&quot;: null,             \&quot;finish_reason\&quot;: \&quot;stop\&quot;         }]         \&quot;usage\&quot;: {             \&quot;prompt_tokens\&quot;: 9,             \&quot;completion_tokens\&quot;: 12,             \&quot;total_tokens\&quot;: 21         }     } }&#39; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **SpendCalculateRequest** | [**SpendCalculateRequest**](../Models/SpendCalculateRequest.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="deleteAllowedIpDeleteAllowedIpPost"></a>
# **deleteAllowedIpDeleteAllowedIpPost**
> oas_any_type_not_mapped deleteAllowedIpDeleteAllowedIpPost(IPAddress)

Delete Allowed Ip

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **IPAddress** | [**IPAddress**](../Models/IPAddress.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="getGlobalSpendReportGlobalSpendReportGet"></a>
# **getGlobalSpendReportGlobalSpendReportGet**
> List getGlobalSpendReportGlobalSpendReportGet(start\_date, end\_date, group\_by, api\_key, internal\_user\_id, team\_id, customer\_id)

Get Global Spend Report

    Get Daily Spend per Team, based on specific startTime and endTime. Per team, view usage by each key, model [     {         \&quot;group-by-day\&quot;: \&quot;2024-05-10\&quot;,         \&quot;teams\&quot;: [             {                 \&quot;team_name\&quot;: \&quot;team-1\&quot;                 \&quot;spend\&quot;: 10,                 \&quot;keys\&quot;: [                     \&quot;key\&quot;: \&quot;1213\&quot;,                     \&quot;usage\&quot;: {                         \&quot;model-1\&quot;: {                                 \&quot;cost\&quot;: 12.50,                                 \&quot;input_tokens\&quot;: 1000,                                 \&quot;output_tokens\&quot;: 5000,                                 \&quot;requests\&quot;: 100                             },                             \&quot;audio-modelname1\&quot;: {                             \&quot;cost\&quot;: 25.50,                             \&quot;seconds\&quot;: 25,                             \&quot;requests\&quot;: 50                     },                     }                 }         ]     ] }

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **start\_date** | **String**| Time from which to start viewing spend | [optional] [default to null] |
| **end\_date** | **String**| Time till which to view spend | [optional] [default to null] |
| **group\_by** | **String**| Group spend by internal team or customer or api_key | [optional] [default to null] [enum: team, customer, api_key] |
| **api\_key** | **String**| View spend for a specific api_key. Example api_key&#x3D;&#39;sk-1234 | [optional] [default to null] |
| **internal\_user\_id** | **String**| View spend for a specific internal_user_id. Example internal_user_id&#x3D;&#39;1234 | [optional] [default to null] |
| **team\_id** | **String**| View spend for a specific team_id. Example team_id&#x3D;&#39;1234 | [optional] [default to null] |
| **customer\_id** | **String**| View spend for a specific customer_id. Example customer_id&#x3D;&#39;1234. Can be used in conjunction with team_id as well. | [optional] [default to null] |

### Return type

[**List**](../Models/LiteLLM_SpendLogs.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getUserDailyActivityUserDailyActivityGet"></a>
# **getUserDailyActivityUserDailyActivityGet**
> SpendAnalyticsPaginatedResponse getUserDailyActivityUserDailyActivityGet(start\_date, end\_date, model, api\_key, page, page\_size)

Get User Daily Activity

    [BETA] This is a beta endpoint. It will change.  Meant to optimize querying spend data for analytics for a user.  Returns: (by date) - spend - prompt_tokens - completion_tokens - cache_read_input_tokens - cache_creation_input_tokens - total_tokens - api_requests - breakdown by model, api_key, provider

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **start\_date** | **String**| Start date in YYYY-MM-DD format | [optional] [default to null] |
| **end\_date** | **String**| End date in YYYY-MM-DD format | [optional] [default to null] |
| **model** | **String**| Filter by specific model | [optional] [default to null] |
| **api\_key** | **String**| Filter by specific API key | [optional] [default to null] |
| **page** | **Integer**| Page number for pagination | [optional] [default to 1] |
| **page\_size** | **Integer**| Items per page | [optional] [default to 50] |

### Return type

[**SpendAnalyticsPaginatedResponse**](../Models/SpendAnalyticsPaginatedResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="globalSpendResetGlobalSpendResetPost"></a>
# **globalSpendResetGlobalSpendResetPost**
> oas_any_type_not_mapped globalSpendResetGlobalSpendResetPost()

Global Spend Reset

    ADMIN ONLY / MASTER KEY Only Endpoint  Globally reset spend for All API Keys and Teams, maintain LiteLLM_SpendLogs  1. LiteLLM_SpendLogs will maintain the logs on spend, no data gets deleted from there 2. LiteLLM_VerificationTokens spend will be set &#x3D; 0 3. LiteLLM_TeamTable spend will be set &#x3D; 0

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="globalViewSpendTagsGlobalSpendTagsGet"></a>
# **globalViewSpendTagsGlobalSpendTagsGet**
> List globalViewSpendTagsGlobalSpendTagsGet(start\_date, end\_date, tags)

Global View Spend Tags

    LiteLLM Enterprise - View Spend Per Request Tag. Used by LiteLLM UI  Example Request: &#x60;&#x60;&#x60; curl -X GET \&quot;http://0.0.0.0:4000/spend/tags\&quot; -H \&quot;Authorization: Bearer sk-1234\&quot; &#x60;&#x60;&#x60;  Spend with Start Date and End Date &#x60;&#x60;&#x60; curl -X GET \&quot;http://0.0.0.0:4000/spend/tags?start_date&#x3D;2022-01-01&amp;end_date&#x3D;2022-02-01\&quot; -H \&quot;Authorization: Bearer sk-1234\&quot; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **start\_date** | **String**| Time from which to start viewing key spend | [optional] [default to null] |
| **end\_date** | **String**| Time till which to view key spend | [optional] [default to null] |
| **tags** | **String**| comman separated tags to filter on | [optional] [default to null] |

### Return type

[**List**](../Models/LiteLLM_SpendLogs.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="viewSpendLogsSpendLogsGet"></a>
# **viewSpendLogsSpendLogsGet**
> List viewSpendLogsSpendLogsGet(api\_key, user\_id, request\_id, start\_date, end\_date)

View Spend Logs

    View all spend logs, if request_id is provided, only logs for that request_id will be returned  Example Request for all logs &#x60;&#x60;&#x60; curl -X GET \&quot;http://0.0.0.0:8000/spend/logs\&quot; -H \&quot;Authorization: Bearer sk-1234\&quot; &#x60;&#x60;&#x60;  Example Request for specific request_id &#x60;&#x60;&#x60; curl -X GET \&quot;http://0.0.0.0:8000/spend/logs?request_id&#x3D;chatcmpl-6dcb2540-d3d7-4e49-bb27-291f863f112e\&quot; -H \&quot;Authorization: Bearer sk-1234\&quot; &#x60;&#x60;&#x60;  Example Request for specific api_key &#x60;&#x60;&#x60; curl -X GET \&quot;http://0.0.0.0:8000/spend/logs?api_key&#x3D;sk-Fn8Ej39NkBQmUagFEoUWPQ\&quot; -H \&quot;Authorization: Bearer sk-1234\&quot; &#x60;&#x60;&#x60;  Example Request for specific user_id &#x60;&#x60;&#x60; curl -X GET \&quot;http://0.0.0.0:8000/spend/logs?user_id&#x3D;ishaan@berri.ai\&quot; -H \&quot;Authorization: Bearer sk-1234\&quot; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **api\_key** | **String**| Get spend logs based on api key | [optional] [default to null] |
| **user\_id** | **String**| Get spend logs based on user_id | [optional] [default to null] |
| **request\_id** | **String**| request_id to get spend logs for specific request_id. If none passed then pass spend logs for all requests | [optional] [default to null] |
| **start\_date** | **String**| Time from which to start viewing key spend | [optional] [default to null] |
| **end\_date** | **String**| Time till which to view key spend | [optional] [default to null] |

### Return type

[**List**](../Models/LiteLLM_SpendLogs.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="viewSpendTagsSpendTagsGet"></a>
# **viewSpendTagsSpendTagsGet**
> List viewSpendTagsSpendTagsGet(start\_date, end\_date)

View Spend Tags

    LiteLLM Enterprise - View Spend Per Request Tag  Example Request: &#x60;&#x60;&#x60; curl -X GET \&quot;http://0.0.0.0:8000/spend/tags\&quot; -H \&quot;Authorization: Bearer sk-1234\&quot; &#x60;&#x60;&#x60;  Spend with Start Date and End Date &#x60;&#x60;&#x60; curl -X GET \&quot;http://0.0.0.0:8000/spend/tags?start_date&#x3D;2022-01-01&amp;end_date&#x3D;2022-02-01\&quot; -H \&quot;Authorization: Bearer sk-1234\&quot; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **start\_date** | **String**| Time from which to start viewing key spend | [optional] [default to null] |
| **end\_date** | **String**| Time till which to view key spend | [optional] [default to null] |

### Return type

[**List**](../Models/LiteLLM_SpendLogs.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

