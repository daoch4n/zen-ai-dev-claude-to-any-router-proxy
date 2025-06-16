# CredentialManagementApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createCredentialCredentialsPost**](CredentialManagementApi.md#createCredentialCredentialsPost) | **POST** /credentials | Create Credential |
| [**deleteCredentialCredentialsCredentialNameDelete**](CredentialManagementApi.md#deleteCredentialCredentialsCredentialNameDelete) | **DELETE** /credentials/{credential_name} | Delete Credential |
| [**getCredentialCredentialsByModelModelIdGet**](CredentialManagementApi.md#getCredentialCredentialsByModelModelIdGet) | **GET** /credentials/by_model/{model_id} | Get Credential |
| [**getCredentialCredentialsByNameCredentialNameGet**](CredentialManagementApi.md#getCredentialCredentialsByNameCredentialNameGet) | **GET** /credentials/by_name/{credential_name} | Get Credential |
| [**getCredentialsCredentialsGet**](CredentialManagementApi.md#getCredentialsCredentialsGet) | **GET** /credentials | Get Credentials |
| [**updateCredentialCredentialsCredentialNamePatch**](CredentialManagementApi.md#updateCredentialCredentialsCredentialNamePatch) | **PATCH** /credentials/{credential_name} | Update Credential |


<a name="createCredentialCredentialsPost"></a>
# **createCredentialCredentialsPost**
> oas_any_type_not_mapped createCredentialCredentialsPost(CreateCredentialItem)

Create Credential

    [BETA] endpoint. This might change unexpectedly. Stores credential in DB. Reloads credentials in memory.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **CreateCredentialItem** | [**CreateCredentialItem**](../Models/CreateCredentialItem.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="deleteCredentialCredentialsCredentialNameDelete"></a>
# **deleteCredentialCredentialsCredentialNameDelete**
> oas_any_type_not_mapped deleteCredentialCredentialsCredentialNameDelete(credential\_name)

Delete Credential

    [BETA] endpoint. This might change unexpectedly.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **credential\_name** | **String**| The credential name, percent-decoded; may contain slashes | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getCredentialCredentialsByModelModelIdGet"></a>
# **getCredentialCredentialsByModelModelIdGet**
> CredentialItem getCredentialCredentialsByModelModelIdGet(credential\_name, model\_id)

Get Credential

    [BETA] endpoint. This might change unexpectedly.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **credential\_name** | **String**| The credential name, percent-decoded; may contain slashes | [default to null] |
| **model\_id** | **String**|  | [default to null] |

### Return type

[**CredentialItem**](../Models/CredentialItem.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getCredentialCredentialsByNameCredentialNameGet"></a>
# **getCredentialCredentialsByNameCredentialNameGet**
> CredentialItem getCredentialCredentialsByNameCredentialNameGet(credential\_name, model\_id)

Get Credential

    [BETA] endpoint. This might change unexpectedly.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **credential\_name** | **String**| The credential name, percent-decoded; may contain slashes | [default to null] |
| **model\_id** | **String**|  | [optional] [default to null] |

### Return type

[**CredentialItem**](../Models/CredentialItem.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getCredentialsCredentialsGet"></a>
# **getCredentialsCredentialsGet**
> oas_any_type_not_mapped getCredentialsCredentialsGet()

Get Credentials

    [BETA] endpoint. This might change unexpectedly.

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="updateCredentialCredentialsCredentialNamePatch"></a>
# **updateCredentialCredentialsCredentialNamePatch**
> oas_any_type_not_mapped updateCredentialCredentialsCredentialNamePatch(credential\_name, CredentialItem)

Update Credential

    [BETA] endpoint. This might change unexpectedly.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **credential\_name** | **String**| The credential name, percent-decoded; may contain slashes | [default to null] |
| **CredentialItem** | [**CredentialItem**](../Models/CredentialItem.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

