# SCIMV2Api

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createGroupScimV2GroupsPost**](SCIMV2Api.md#createGroupScimV2GroupsPost) | **POST** /scim/v2/Groups | Create Group |
| [**createUserScimV2UsersPost**](SCIMV2Api.md#createUserScimV2UsersPost) | **POST** /scim/v2/Users | Create User |
| [**deleteGroupScimV2GroupsGroupIdDelete**](SCIMV2Api.md#deleteGroupScimV2GroupsGroupIdDelete) | **DELETE** /scim/v2/Groups/{group_id} | Delete Group |
| [**deleteUserScimV2UsersUserIdDelete**](SCIMV2Api.md#deleteUserScimV2UsersUserIdDelete) | **DELETE** /scim/v2/Users/{user_id} | Delete User |
| [**getGroupScimV2GroupsGroupIdGet**](SCIMV2Api.md#getGroupScimV2GroupsGroupIdGet) | **GET** /scim/v2/Groups/{group_id} | Get Group |
| [**getGroupsScimV2GroupsGet**](SCIMV2Api.md#getGroupsScimV2GroupsGet) | **GET** /scim/v2/Groups | Get Groups |
| [**getUserScimV2UsersUserIdGet**](SCIMV2Api.md#getUserScimV2UsersUserIdGet) | **GET** /scim/v2/Users/{user_id} | Get User |
| [**getUsersScimV2UsersGet**](SCIMV2Api.md#getUsersScimV2UsersGet) | **GET** /scim/v2/Users | Get Users |
| [**patchGroupScimV2GroupsGroupIdPatch**](SCIMV2Api.md#patchGroupScimV2GroupsGroupIdPatch) | **PATCH** /scim/v2/Groups/{group_id} | Patch Group |
| [**patchUserScimV2UsersUserIdPatch**](SCIMV2Api.md#patchUserScimV2UsersUserIdPatch) | **PATCH** /scim/v2/Users/{user_id} | Patch User |
| [**updateGroupScimV2GroupsGroupIdPut**](SCIMV2Api.md#updateGroupScimV2GroupsGroupIdPut) | **PUT** /scim/v2/Groups/{group_id} | Update Group |
| [**updateUserScimV2UsersUserIdPut**](SCIMV2Api.md#updateUserScimV2UsersUserIdPut) | **PUT** /scim/v2/Users/{user_id} | Update User |


<a name="createGroupScimV2GroupsPost"></a>
# **createGroupScimV2GroupsPost**
> SCIMGroup createGroupScimV2GroupsPost(SCIMGroup)

Create Group

    Create a group according to SCIM v2 protocol

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **SCIMGroup** | [**SCIMGroup**](../Models/SCIMGroup.md)|  | |

### Return type

[**SCIMGroup**](../Models/SCIMGroup.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="createUserScimV2UsersPost"></a>
# **createUserScimV2UsersPost**
> SCIMUser createUserScimV2UsersPost(SCIMUser)

Create User

    Create a user according to SCIM v2 protocol

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **SCIMUser** | [**SCIMUser**](../Models/SCIMUser.md)|  | |

### Return type

[**SCIMUser**](../Models/SCIMUser.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="deleteGroupScimV2GroupsGroupIdDelete"></a>
# **deleteGroupScimV2GroupsGroupIdDelete**
> deleteGroupScimV2GroupsGroupIdDelete(group\_id)

Delete Group

    Delete a group according to SCIM v2 protocol

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **group\_id** | **String**|  | [default to null] |

### Return type

null (empty response body)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="deleteUserScimV2UsersUserIdDelete"></a>
# **deleteUserScimV2UsersUserIdDelete**
> deleteUserScimV2UsersUserIdDelete(user\_id)

Delete User

    Delete a user according to SCIM v2 protocol

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **user\_id** | **String**|  | [default to null] |

### Return type

null (empty response body)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getGroupScimV2GroupsGroupIdGet"></a>
# **getGroupScimV2GroupsGroupIdGet**
> SCIMGroup getGroupScimV2GroupsGroupIdGet(group\_id)

Get Group

    Get a single group by ID according to SCIM v2 protocol

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **group\_id** | **String**|  | [default to null] |

### Return type

[**SCIMGroup**](../Models/SCIMGroup.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getGroupsScimV2GroupsGet"></a>
# **getGroupsScimV2GroupsGet**
> SCIMListResponse getGroupsScimV2GroupsGet(startIndex, count, filter)

Get Groups

    Get a list of groups according to SCIM v2 protocol

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **startIndex** | **Integer**|  | [optional] [default to 1] |
| **count** | **Integer**|  | [optional] [default to 10] |
| **filter** | **String**|  | [optional] [default to null] |

### Return type

[**SCIMListResponse**](../Models/SCIMListResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getUserScimV2UsersUserIdGet"></a>
# **getUserScimV2UsersUserIdGet**
> SCIMUser getUserScimV2UsersUserIdGet(user\_id)

Get User

    Get a single user by ID according to SCIM v2 protocol

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **user\_id** | **String**|  | [default to null] |

### Return type

[**SCIMUser**](../Models/SCIMUser.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getUsersScimV2UsersGet"></a>
# **getUsersScimV2UsersGet**
> SCIMListResponse getUsersScimV2UsersGet(startIndex, count, filter)

Get Users

    Get a list of users according to SCIM v2 protocol

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **startIndex** | **Integer**|  | [optional] [default to 1] |
| **count** | **Integer**|  | [optional] [default to 10] |
| **filter** | **String**|  | [optional] [default to null] |

### Return type

[**SCIMListResponse**](../Models/SCIMListResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="patchGroupScimV2GroupsGroupIdPatch"></a>
# **patchGroupScimV2GroupsGroupIdPatch**
> SCIMGroup patchGroupScimV2GroupsGroupIdPatch(group\_id, SCIMPatchOp)

Patch Group

    Patch a group according to SCIM v2 protocol

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **group\_id** | **String**|  | [default to null] |
| **SCIMPatchOp** | [**SCIMPatchOp**](../Models/SCIMPatchOp.md)|  | |

### Return type

[**SCIMGroup**](../Models/SCIMGroup.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="patchUserScimV2UsersUserIdPatch"></a>
# **patchUserScimV2UsersUserIdPatch**
> SCIMUser patchUserScimV2UsersUserIdPatch(user\_id, SCIMPatchOp)

Patch User

    Patch a user according to SCIM v2 protocol

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **user\_id** | **String**|  | [default to null] |
| **SCIMPatchOp** | [**SCIMPatchOp**](../Models/SCIMPatchOp.md)|  | |

### Return type

[**SCIMUser**](../Models/SCIMUser.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="updateGroupScimV2GroupsGroupIdPut"></a>
# **updateGroupScimV2GroupsGroupIdPut**
> SCIMGroup updateGroupScimV2GroupsGroupIdPut(group\_id, SCIMGroup)

Update Group

    Update a group according to SCIM v2 protocol

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **group\_id** | **String**|  | [default to null] |
| **SCIMGroup** | [**SCIMGroup**](../Models/SCIMGroup.md)|  | |

### Return type

[**SCIMGroup**](../Models/SCIMGroup.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="updateUserScimV2UsersUserIdPut"></a>
# **updateUserScimV2UsersUserIdPut**
> SCIMUser updateUserScimV2UsersUserIdPut(user\_id, SCIMUser)

Update User

    Update a user according to SCIM v2 protocol

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **user\_id** | **String**|  | [default to null] |
| **SCIMUser** | [**SCIMUser**](../Models/SCIMUser.md)|  | |

### Return type

[**SCIMUser**](../Models/SCIMUser.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

