# EmailManagementApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getEmailEventSettingsEmailEventSettingsGet**](EmailManagementApi.md#getEmailEventSettingsEmailEventSettingsGet) | **GET** /email/event_settings | Get Email Event Settings |
| [**resetEventSettingsEmailEventSettingsResetPost**](EmailManagementApi.md#resetEventSettingsEmailEventSettingsResetPost) | **POST** /email/event_settings/reset | Reset Event Settings |
| [**updateEventSettingsEmailEventSettingsPatch**](EmailManagementApi.md#updateEventSettingsEmailEventSettingsPatch) | **PATCH** /email/event_settings | Update Event Settings |


<a name="getEmailEventSettingsEmailEventSettingsGet"></a>
# **getEmailEventSettingsEmailEventSettingsGet**
> EmailEventSettingsResponse getEmailEventSettingsEmailEventSettingsGet()

Get Email Event Settings

    Get all email event settings

### Parameters
This endpoint does not need any parameter.

### Return type

[**EmailEventSettingsResponse**](../Models/EmailEventSettingsResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="resetEventSettingsEmailEventSettingsResetPost"></a>
# **resetEventSettingsEmailEventSettingsResetPost**
> oas_any_type_not_mapped resetEventSettingsEmailEventSettingsResetPost()

Reset Event Settings

    Reset all email event settings to default (new user invitations on, virtual key creation off)

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="updateEventSettingsEmailEventSettingsPatch"></a>
# **updateEventSettingsEmailEventSettingsPatch**
> oas_any_type_not_mapped updateEventSettingsEmailEventSettingsPatch(EmailEventSettingsUpdateRequest)

Update Event Settings

    Update the settings for email events

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **EmailEventSettingsUpdateRequest** | [**EmailEventSettingsUpdateRequest**](../Models/EmailEventSettingsUpdateRequest.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

