# DefaultApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createPassThroughEndpointsConfigPassThroughEndpointPost**](DefaultApi.md#createPassThroughEndpointsConfigPassThroughEndpointPost) | **POST** /config/pass_through_endpoint | Create Pass Through Endpoints |
| [**deletePassThroughEndpointsConfigPassThroughEndpointDelete**](DefaultApi.md#deletePassThroughEndpointsConfigPassThroughEndpointDelete) | **DELETE** /config/pass_through_endpoint | Delete Pass Through Endpoints |
| [**getActiveTasksStatsDebugAsyncioTasksGet**](DefaultApi.md#getActiveTasksStatsDebugAsyncioTasksGet) | **GET** /debug/asyncio-tasks | Get Active Tasks Stats |
| [**getPassThroughEndpointsConfigPassThroughEndpointGet**](DefaultApi.md#getPassThroughEndpointsConfigPassThroughEndpointGet) | **GET** /config/pass_through_endpoint | Get Pass Through Endpoints |
| [**getRobotsRobotsTxtGet**](DefaultApi.md#getRobotsRobotsTxtGet) | **GET** /robots.txt | Get Robots |
| [**getRoutesRoutesGet**](DefaultApi.md#getRoutesRoutesGet) | **GET** /routes | Get Routes |
| [**getUiConfigLitellmWellKnownLitellmUiConfigGet**](DefaultApi.md#getUiConfigLitellmWellKnownLitellmUiConfigGet) | **GET** /litellm/.well-known/litellm-ui-config | Get Ui Config |
| [**getUiConfigWellKnownLitellmUiConfigGet**](DefaultApi.md#getUiConfigWellKnownLitellmUiConfigGet) | **GET** /.well-known/litellm-ui-config | Get Ui Config |
| [**homeGet**](DefaultApi.md#homeGet) | **GET** / | Home |
| [**listAvailableTeamsTeamAvailableGet**](DefaultApi.md#listAvailableTeamsTeamAvailableGet) | **GET** /team/available | List Available Teams |
| [**providerBudgetsProviderBudgetsGet**](DefaultApi.md#providerBudgetsProviderBudgetsGet) | **GET** /provider/budgets | Provider Budgets |
| [**updatePassThroughEndpointsConfigPassThroughEndpointEndpointIdPost**](DefaultApi.md#updatePassThroughEndpointsConfigPassThroughEndpointEndpointIdPost) | **POST** /config/pass_through_endpoint/{endpoint_id} | Update Pass Through Endpoints |


<a name="createPassThroughEndpointsConfigPassThroughEndpointPost"></a>
# **createPassThroughEndpointsConfigPassThroughEndpointPost**
> oas_any_type_not_mapped createPassThroughEndpointsConfigPassThroughEndpointPost(PassThroughGenericEndpoint)

Create Pass Through Endpoints

    Create new pass-through endpoint

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **PassThroughGenericEndpoint** | [**PassThroughGenericEndpoint**](../Models/PassThroughGenericEndpoint.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="deletePassThroughEndpointsConfigPassThroughEndpointDelete"></a>
# **deletePassThroughEndpointsConfigPassThroughEndpointDelete**
> PassThroughEndpointResponse deletePassThroughEndpointsConfigPassThroughEndpointDelete(endpoint\_id)

Delete Pass Through Endpoints

    Delete a pass-through endpoint  Returns - the deleted endpoint

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **endpoint\_id** | **String**|  | [default to null] |

### Return type

[**PassThroughEndpointResponse**](../Models/PassThroughEndpointResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getActiveTasksStatsDebugAsyncioTasksGet"></a>
# **getActiveTasksStatsDebugAsyncioTasksGet**
> oas_any_type_not_mapped getActiveTasksStatsDebugAsyncioTasksGet()

Get Active Tasks Stats

    Returns:   total_active_tasks: int   by_name: { coroutine_name: count }

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getPassThroughEndpointsConfigPassThroughEndpointGet"></a>
# **getPassThroughEndpointsConfigPassThroughEndpointGet**
> PassThroughEndpointResponse getPassThroughEndpointsConfigPassThroughEndpointGet(endpoint\_id)

Get Pass Through Endpoints

    GET configured pass through endpoint.  If no endpoint_id given, return all configured endpoints.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **endpoint\_id** | **String**|  | [optional] [default to null] |

### Return type

[**PassThroughEndpointResponse**](../Models/PassThroughEndpointResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getRobotsRobotsTxtGet"></a>
# **getRobotsRobotsTxtGet**
> oas_any_type_not_mapped getRobotsRobotsTxtGet()

Get Robots

    Block all web crawlers from indexing the proxy server endpoints This is useful for ensuring that the API endpoints aren&#39;t indexed by search engines

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getRoutesRoutesGet"></a>
# **getRoutesRoutesGet**
> oas_any_type_not_mapped getRoutesRoutesGet()

Get Routes

    Get a list of available routes in the FastAPI application.

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getUiConfigLitellmWellKnownLitellmUiConfigGet"></a>
# **getUiConfigLitellmWellKnownLitellmUiConfigGet**
> UiDiscoveryEndpoints getUiConfigLitellmWellKnownLitellmUiConfigGet()

Get Ui Config

### Parameters
This endpoint does not need any parameter.

### Return type

[**UiDiscoveryEndpoints**](../Models/UiDiscoveryEndpoints.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getUiConfigWellKnownLitellmUiConfigGet"></a>
# **getUiConfigWellKnownLitellmUiConfigGet**
> UiDiscoveryEndpoints getUiConfigWellKnownLitellmUiConfigGet()

Get Ui Config

### Parameters
This endpoint does not need any parameter.

### Return type

[**UiDiscoveryEndpoints**](../Models/UiDiscoveryEndpoints.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="homeGet"></a>
# **homeGet**
> oas_any_type_not_mapped homeGet()

Home

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="listAvailableTeamsTeamAvailableGet"></a>
# **listAvailableTeamsTeamAvailableGet**
> oas_any_type_not_mapped listAvailableTeamsTeamAvailableGet(response\_model)

List Available Teams

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **response\_model** | [**oas_any_type_not_mapped**](../Models/.md)|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="providerBudgetsProviderBudgetsGet"></a>
# **providerBudgetsProviderBudgetsGet**
> ProviderBudgetResponse providerBudgetsProviderBudgetsGet()

Provider Budgets

    Provider Budget Routing - Get Budget, Spend Details https://docs.litellm.ai/docs/proxy/provider_budget_routing  Use this endpoint to check current budget, spend and budget reset time for a provider  Example Request  &#x60;&#x60;&#x60;bash curl -X GET http://localhost:4000/provider/budgets     -H \&quot;Content-Type: application/json\&quot;     -H \&quot;Authorization: Bearer sk-1234\&quot; &#x60;&#x60;&#x60;  Example Response  &#x60;&#x60;&#x60;json {     \&quot;providers\&quot;: {         \&quot;openai\&quot;: {             \&quot;budget_limit\&quot;: 1e-12,             \&quot;time_period\&quot;: \&quot;1d\&quot;,             \&quot;spend\&quot;: 0.0,             \&quot;budget_reset_at\&quot;: null         },         \&quot;azure\&quot;: {             \&quot;budget_limit\&quot;: 100.0,             \&quot;time_period\&quot;: \&quot;1d\&quot;,             \&quot;spend\&quot;: 0.0,             \&quot;budget_reset_at\&quot;: null         },         \&quot;anthropic\&quot;: {             \&quot;budget_limit\&quot;: 100.0,             \&quot;time_period\&quot;: \&quot;10d\&quot;,             \&quot;spend\&quot;: 0.0,             \&quot;budget_reset_at\&quot;: null         },         \&quot;vertex_ai\&quot;: {             \&quot;budget_limit\&quot;: 100.0,             \&quot;time_period\&quot;: \&quot;12d\&quot;,             \&quot;spend\&quot;: 0.0,             \&quot;budget_reset_at\&quot;: null         }     } } &#x60;&#x60;&#x60;

### Parameters
This endpoint does not need any parameter.

### Return type

[**ProviderBudgetResponse**](../Models/ProviderBudgetResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="updatePassThroughEndpointsConfigPassThroughEndpointEndpointIdPost"></a>
# **updatePassThroughEndpointsConfigPassThroughEndpointEndpointIdPost**
> oas_any_type_not_mapped updatePassThroughEndpointsConfigPassThroughEndpointEndpointIdPost(endpoint\_id)

Update Pass Through Endpoints

    Update a pass-through endpoint

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **endpoint\_id** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

