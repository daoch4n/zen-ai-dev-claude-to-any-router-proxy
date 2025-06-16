# HealthApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**activeCallbacksActiveCallbacksGet**](HealthApi.md#activeCallbacksActiveCallbacksGet) | **GET** /active/callbacks | Active Callbacks |
| [**activeCallbacksSettingsGet**](HealthApi.md#activeCallbacksSettingsGet) | **GET** /settings | Active Callbacks |
| [**healthEndpointHealthGet**](HealthApi.md#healthEndpointHealthGet) | **GET** /health | Health Endpoint |
| [**healthLivelinessHealthLivelinessGet**](HealthApi.md#healthLivelinessHealthLivelinessGet) | **GET** /health/liveliness | Health Liveliness |
| [**healthLivelinessHealthLivenessGet**](HealthApi.md#healthLivelinessHealthLivenessGet) | **GET** /health/liveness | Health Liveliness |
| [**healthLivelinessOptionsHealthLivelinessOptions**](HealthApi.md#healthLivelinessOptionsHealthLivelinessOptions) | **OPTIONS** /health/liveliness | Health Liveliness Options |
| [**healthLivelinessOptionsHealthLivenessOptions**](HealthApi.md#healthLivelinessOptionsHealthLivenessOptions) | **OPTIONS** /health/liveness | Health Liveliness Options |
| [**healthReadinessHealthReadinessGet**](HealthApi.md#healthReadinessHealthReadinessGet) | **GET** /health/readiness | Health Readiness |
| [**healthReadinessOptionsHealthReadinessOptions**](HealthApi.md#healthReadinessOptionsHealthReadinessOptions) | **OPTIONS** /health/readiness | Health Readiness Options |
| [**healthServicesEndpointHealthServicesGet**](HealthApi.md#healthServicesEndpointHealthServicesGet) | **GET** /health/services | Health Services Endpoint |
| [**testEndpointTestGet**](HealthApi.md#testEndpointTestGet) | **GET** /test | Test Endpoint |
| [**testModelConnectionHealthTestConnectionPost**](HealthApi.md#testModelConnectionHealthTestConnectionPost) | **POST** /health/test_connection | Test Model Connection |


<a name="activeCallbacksActiveCallbacksGet"></a>
# **activeCallbacksActiveCallbacksGet**
> oas_any_type_not_mapped activeCallbacksActiveCallbacksGet()

Active Callbacks

    Returns a list of litellm level settings  This is useful for debugging and ensuring the proxy server is configured correctly.  Response schema: &#x60;&#x60;&#x60; {     \&quot;alerting\&quot;: _alerting,     \&quot;litellm.callbacks\&quot;: litellm_callbacks,     \&quot;litellm.input_callback\&quot;: litellm_input_callbacks,     \&quot;litellm.failure_callback\&quot;: litellm_failure_callbacks,     \&quot;litellm.success_callback\&quot;: litellm_success_callbacks,     \&quot;litellm._async_success_callback\&quot;: litellm_async_success_callbacks,     \&quot;litellm._async_failure_callback\&quot;: litellm_async_failure_callbacks,     \&quot;litellm._async_input_callback\&quot;: litellm_async_input_callbacks,     \&quot;all_litellm_callbacks\&quot;: all_litellm_callbacks,     \&quot;num_callbacks\&quot;: len(all_litellm_callbacks),     \&quot;num_alerting\&quot;: _num_alerting,     \&quot;litellm.request_timeout\&quot;: litellm.request_timeout, } &#x60;&#x60;&#x60;

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="activeCallbacksSettingsGet"></a>
# **activeCallbacksSettingsGet**
> oas_any_type_not_mapped activeCallbacksSettingsGet()

Active Callbacks

    Returns a list of litellm level settings  This is useful for debugging and ensuring the proxy server is configured correctly.  Response schema: &#x60;&#x60;&#x60; {     \&quot;alerting\&quot;: _alerting,     \&quot;litellm.callbacks\&quot;: litellm_callbacks,     \&quot;litellm.input_callback\&quot;: litellm_input_callbacks,     \&quot;litellm.failure_callback\&quot;: litellm_failure_callbacks,     \&quot;litellm.success_callback\&quot;: litellm_success_callbacks,     \&quot;litellm._async_success_callback\&quot;: litellm_async_success_callbacks,     \&quot;litellm._async_failure_callback\&quot;: litellm_async_failure_callbacks,     \&quot;litellm._async_input_callback\&quot;: litellm_async_input_callbacks,     \&quot;all_litellm_callbacks\&quot;: all_litellm_callbacks,     \&quot;num_callbacks\&quot;: len(all_litellm_callbacks),     \&quot;num_alerting\&quot;: _num_alerting,     \&quot;litellm.request_timeout\&quot;: litellm.request_timeout, } &#x60;&#x60;&#x60;

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="healthEndpointHealthGet"></a>
# **healthEndpointHealthGet**
> oas_any_type_not_mapped healthEndpointHealthGet(model)

Health Endpoint

    🚨 USE &#x60;/health/liveliness&#x60; to health check the proxy 🚨  See more 👉 https://docs.litellm.ai/docs/proxy/health   Check the health of all the endpoints in config.yaml  To run health checks in the background, add this to config.yaml: &#x60;&#x60;&#x60; general_settings:     # ... other settings     background_health_checks: True &#x60;&#x60;&#x60; else, the health checks will be run on models when /health is called.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **model** | **String**| Specify the model name (optional) | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="healthLivelinessHealthLivelinessGet"></a>
# **healthLivelinessHealthLivelinessGet**
> oas_any_type_not_mapped healthLivelinessHealthLivelinessGet()

Health Liveliness

    Unprotected endpoint for checking if worker is alive

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="healthLivelinessHealthLivenessGet"></a>
# **healthLivelinessHealthLivenessGet**
> oas_any_type_not_mapped healthLivelinessHealthLivenessGet()

Health Liveliness

    Unprotected endpoint for checking if worker is alive

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="healthLivelinessOptionsHealthLivelinessOptions"></a>
# **healthLivelinessOptionsHealthLivelinessOptions**
> oas_any_type_not_mapped healthLivelinessOptionsHealthLivelinessOptions()

Health Liveliness Options

    Options endpoint for health/liveliness check.

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="healthLivelinessOptionsHealthLivenessOptions"></a>
# **healthLivelinessOptionsHealthLivenessOptions**
> oas_any_type_not_mapped healthLivelinessOptionsHealthLivenessOptions()

Health Liveliness Options

    Options endpoint for health/liveliness check.

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="healthReadinessHealthReadinessGet"></a>
# **healthReadinessHealthReadinessGet**
> oas_any_type_not_mapped healthReadinessHealthReadinessGet()

Health Readiness

    Unprotected endpoint for checking if worker can receive requests

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="healthReadinessOptionsHealthReadinessOptions"></a>
# **healthReadinessOptionsHealthReadinessOptions**
> oas_any_type_not_mapped healthReadinessOptionsHealthReadinessOptions()

Health Readiness Options

    Options endpoint for health/readiness check.

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="healthServicesEndpointHealthServicesGet"></a>
# **healthServicesEndpointHealthServicesGet**
> oas_any_type_not_mapped healthServicesEndpointHealthServicesGet(service)

Health Services Endpoint

    Use this admin-only endpoint to check if the service is healthy.  Example: &#x60;&#x60;&#x60; curl -L -X GET &#39;http://0.0.0.0:4000/health/services?service&#x3D;datadog&#39;     -H &#39;Authorization: Bearer sk-1234&#39; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **service** | [**Service**](../Models/.md)| Specify the service being hit. | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="testEndpointTestGet"></a>
# **testEndpointTestGet**
> oas_any_type_not_mapped testEndpointTestGet()

Test Endpoint

    [DEPRECATED] use &#x60;/health/liveliness&#x60; instead.  A test endpoint that pings the proxy server to check if it&#39;s healthy.  Parameters:     request (Request): The incoming request.  Returns:     dict: A dictionary containing the route of the request URL.

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="testModelConnectionHealthTestConnectionPost"></a>
# **testModelConnectionHealthTestConnectionPost**
> oas_any_type_not_mapped testModelConnectionHealthTestConnectionPost(Body\_test\_model\_connection\_health\_test\_connection\_post)

Test Model Connection

    Test a direct connection to a specific model.  This endpoint allows you to verify if your proxy can successfully connect to a specific model. It&#39;s useful for troubleshooting model connectivity issues without going through the full proxy routing.  Example: &#x60;&#x60;&#x60;bash curl -X POST &#39;http://localhost:4000/health/test_connection&#39; \\   -H &#39;Authorization: Bearer sk-1234&#39; \\   -H &#39;Content-Type: application/json&#39; \\   -d &#39;{     \&quot;litellm_params\&quot;: {         \&quot;model\&quot;: \&quot;gpt-4\&quot;,         \&quot;custom_llm_provider\&quot;: \&quot;azure_ai\&quot;,         \&quot;litellm_credential_name\&quot;: null,         \&quot;api_key\&quot;: \&quot;6xxxxxxx\&quot;,         \&quot;api_base\&quot;: \&quot;https://litellm8397336933.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version&#x3D;2024-10-21\&quot;,     },     \&quot;mode\&quot;: \&quot;chat\&quot;   }&#39; &#x60;&#x60;&#x60;  Returns:     dict: A dictionary containing the health check result with either success information or error details.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **Body\_test\_model\_connection\_health\_test\_connection\_post** | [**Body_test_model_connection_health_test_connection_post**](../Models/Body_test_model_connection_health_test_connection_post.md)|  | [optional] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

