# SSOSettingsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getDefaultTeamSettingsGetDefaultTeamSettingsGet**](SSOSettingsApi.md#getDefaultTeamSettingsGetDefaultTeamSettingsGet) | **GET** /get/default_team_settings | Get Default Team Settings |
| [**getInternalUserSettingsGetInternalUserSettingsGet**](SSOSettingsApi.md#getInternalUserSettingsGetInternalUserSettingsGet) | **GET** /get/internal_user_settings | Get Internal User Settings |
| [**getSsoSettingsGetSsoSettingsGet**](SSOSettingsApi.md#getSsoSettingsGetSsoSettingsGet) | **GET** /get/sso_settings | Get Sso Settings |
| [**updateDefaultTeamSettingsUpdateDefaultTeamSettingsPatch**](SSOSettingsApi.md#updateDefaultTeamSettingsUpdateDefaultTeamSettingsPatch) | **PATCH** /update/default_team_settings | Update Default Team Settings |
| [**updateInternalUserSettingsUpdateInternalUserSettingsPatch**](SSOSettingsApi.md#updateInternalUserSettingsUpdateInternalUserSettingsPatch) | **PATCH** /update/internal_user_settings | Update Internal User Settings |
| [**updateSsoSettingsUpdateSsoSettingsPatch**](SSOSettingsApi.md#updateSsoSettingsUpdateSsoSettingsPatch) | **PATCH** /update/sso_settings | Update Sso Settings |


<a name="getDefaultTeamSettingsGetDefaultTeamSettingsGet"></a>
# **getDefaultTeamSettingsGetDefaultTeamSettingsGet**
> DefaultTeamSettingsResponse getDefaultTeamSettingsGetDefaultTeamSettingsGet()

Get Default Team Settings

    Get all SSO settings from the litellm_settings configuration. Returns a structured object with values and descriptions for UI display.

### Parameters
This endpoint does not need any parameter.

### Return type

[**DefaultTeamSettingsResponse**](../Models/DefaultTeamSettingsResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getInternalUserSettingsGetInternalUserSettingsGet"></a>
# **getInternalUserSettingsGetInternalUserSettingsGet**
> InternalUserSettingsResponse getInternalUserSettingsGetInternalUserSettingsGet()

Get Internal User Settings

    Get all SSO settings from the litellm_settings configuration. Returns a structured object with values and descriptions for UI display.

### Parameters
This endpoint does not need any parameter.

### Return type

[**InternalUserSettingsResponse**](../Models/InternalUserSettingsResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getSsoSettingsGetSsoSettingsGet"></a>
# **getSsoSettingsGetSsoSettingsGet**
> SSOSettingsResponse getSsoSettingsGetSsoSettingsGet()

Get Sso Settings

    Get all SSO configuration settings from the environment variables. Returns a structured object with values and descriptions for UI display.

### Parameters
This endpoint does not need any parameter.

### Return type

[**SSOSettingsResponse**](../Models/SSOSettingsResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="updateDefaultTeamSettingsUpdateDefaultTeamSettingsPatch"></a>
# **updateDefaultTeamSettingsUpdateDefaultTeamSettingsPatch**
> oas_any_type_not_mapped updateDefaultTeamSettingsUpdateDefaultTeamSettingsPatch(DefaultTeamSSOParams)

Update Default Team Settings

    Update the default team parameters for SSO users. These settings will be applied to new teams created from SSO.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **DefaultTeamSSOParams** | [**DefaultTeamSSOParams**](../Models/DefaultTeamSSOParams.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="updateInternalUserSettingsUpdateInternalUserSettingsPatch"></a>
# **updateInternalUserSettingsUpdateInternalUserSettingsPatch**
> oas_any_type_not_mapped updateInternalUserSettingsUpdateInternalUserSettingsPatch(DefaultInternalUserParams)

Update Internal User Settings

    Update the default internal user parameters for SSO users. These settings will be applied to new users who sign in via SSO.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **DefaultInternalUserParams** | [**DefaultInternalUserParams**](../Models/DefaultInternalUserParams.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="updateSsoSettingsUpdateSsoSettingsPatch"></a>
# **updateSsoSettingsUpdateSsoSettingsPatch**
> oas_any_type_not_mapped updateSsoSettingsUpdateSsoSettingsPatch(SSOConfig)

Update Sso Settings

    Update SSO configuration by saving to both environment variables and config file.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **SSOConfig** | [**SSOConfig**](../Models/SSOConfig.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

