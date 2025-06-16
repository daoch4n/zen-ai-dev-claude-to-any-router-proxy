# ModerationsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**moderationsModerationsPost**](ModerationsApi.md#moderationsModerationsPost) | **POST** /moderations | Moderations |
| [**moderationsV1ModerationsPost**](ModerationsApi.md#moderationsV1ModerationsPost) | **POST** /v1/moderations | Moderations |


<a name="moderationsModerationsPost"></a>
# **moderationsModerationsPost**
> oas_any_type_not_mapped moderationsModerationsPost()

Moderations

    The moderations endpoint is a tool you can use to check whether content complies with an LLM Providers policies. Quick Start &#x60;&#x60;&#x60; curl --location &#39;http://0.0.0.0:4000/moderations&#39;     --header &#39;Content-Type: application/json&#39;     --header &#39;Authorization: Bearer sk-1234&#39;     --data &#39;{\&quot;input\&quot;: \&quot;Sample text goes here\&quot;, \&quot;model\&quot;: \&quot;text-moderation-stable\&quot;}&#39; &#x60;&#x60;&#x60;

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="moderationsV1ModerationsPost"></a>
# **moderationsV1ModerationsPost**
> oas_any_type_not_mapped moderationsV1ModerationsPost()

Moderations

    The moderations endpoint is a tool you can use to check whether content complies with an LLM Providers policies. Quick Start &#x60;&#x60;&#x60; curl --location &#39;http://0.0.0.0:4000/moderations&#39;     --header &#39;Content-Type: application/json&#39;     --header &#39;Authorization: Bearer sk-1234&#39;     --data &#39;{\&quot;input\&quot;: \&quot;Sample text goes here\&quot;, \&quot;model\&quot;: \&quot;text-moderation-stable\&quot;}&#39; &#x60;&#x60;&#x60;

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

