# InternalUserManagementApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**deleteUserUserDeletePost**](InternalUserManagementApi.md#deleteUserUserDeletePost) | **POST** /user/delete | Delete User |
| [**getUserDailyActivityUserDailyActivityGet**](InternalUserManagementApi.md#getUserDailyActivityUserDailyActivityGet) | **GET** /user/daily/activity | Get User Daily Activity |
| [**getUsersUserListGet**](InternalUserManagementApi.md#getUsersUserListGet) | **GET** /user/list | Get Users |
| [**newUserUserNewPost**](InternalUserManagementApi.md#newUserUserNewPost) | **POST** /user/new | New User |
| [**userInfoUserInfoGet**](InternalUserManagementApi.md#userInfoUserInfoGet) | **GET** /user/info | User Info |
| [**userUpdateUserUpdatePost**](InternalUserManagementApi.md#userUpdateUserUpdatePost) | **POST** /user/update | User Update |


<a name="deleteUserUserDeletePost"></a>
# **deleteUserUserDeletePost**
> oas_any_type_not_mapped deleteUserUserDeletePost(DeleteUserRequest, litellm-changed-by)

Delete User

    delete user and associated user keys  &#x60;&#x60;&#x60; curl --location &#39;http://0.0.0.0:4000/user/delete&#39;  --header &#39;Authorization: Bearer sk-1234&#39;  --header &#39;Content-Type: application/json&#39;  --data-raw &#39;{     \&quot;user_ids\&quot;: [\&quot;45e3e396-ee08-4a61-a88e-16b3ce7e0849\&quot;] }&#39; &#x60;&#x60;&#x60;  Parameters: - user_ids: List[str] - The list of user id&#39;s to be deleted.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **DeleteUserRequest** | [**DeleteUserRequest**](../Models/DeleteUserRequest.md)|  | |
| **litellm-changed-by** | **String**| The litellm-changed-by header enables tracking of actions performed by authorized users on behalf of other users, providing an audit trail for accountability | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
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

<a name="getUsersUserListGet"></a>
# **getUsersUserListGet**
> UserListResponse getUsersUserListGet(role, user\_ids, sso\_user\_ids, user\_email, team, page, page\_size, sort\_by, sort\_order)

Get Users

    Get a paginated list of users with filtering and sorting options.  Parameters:     role: Optional[str]         Filter users by role. Can be one of:         - proxy_admin         - proxy_admin_viewer         - internal_user         - internal_user_viewer     user_ids: Optional[str]         Get list of users by user_ids. Comma separated list of user_ids.     sso_ids: Optional[str]         Get list of users by sso_ids. Comma separated list of sso_ids.     user_email: Optional[str]         Filter users by partial email match     team: Optional[str]         Filter users by team id. Will match if user has this team in their teams array.     page: int         The page number to return     page_size: int         The number of items per page     sort_by: Optional[str]         Column to sort by (e.g. &#39;user_id&#39;, &#39;user_email&#39;, &#39;created_at&#39;, &#39;spend&#39;)     sort_order: Optional[str]         Sort order (&#39;asc&#39; or &#39;desc&#39;)

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **role** | **String**| Filter users by role | [optional] [default to null] |
| **user\_ids** | **String**| Get list of users by user_ids | [optional] [default to null] |
| **sso\_user\_ids** | **String**| Get list of users by sso_user_id | [optional] [default to null] |
| **user\_email** | **String**| Filter users by partial email match | [optional] [default to null] |
| **team** | **String**| Filter users by team id | [optional] [default to null] |
| **page** | **Integer**| Page number | [optional] [default to 1] |
| **page\_size** | **Integer**| Number of items per page | [optional] [default to 25] |
| **sort\_by** | **String**| Column to sort by (e.g. &#39;user_id&#39;, &#39;user_email&#39;, &#39;created_at&#39;, &#39;spend&#39;) | [optional] [default to null] |
| **sort\_order** | **String**| Sort order (&#39;asc&#39; or &#39;desc&#39;) | [optional] [default to asc] |

### Return type

[**UserListResponse**](../Models/UserListResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="newUserUserNewPost"></a>
# **newUserUserNewPost**
> NewUserResponse newUserUserNewPost(NewUserRequest)

New User

    Use this to create a new INTERNAL user with a budget. Internal Users can access LiteLLM Admin UI to make keys, request access to models. This creates a new user and generates a new api key for the new user. The new api key is returned.  Returns user id, budget + new key.  Parameters: - user_id: Optional[str] - Specify a user id. If not set, a unique id will be generated. - user_alias: Optional[str] - A descriptive name for you to know who this user id refers to. - teams: Optional[list] - specify a list of team id&#39;s a user belongs to. - user_email: Optional[str] - Specify a user email. - send_invite_email: Optional[bool] - Specify if an invite email should be sent. - user_role: Optional[str] - Specify a user role - \&quot;proxy_admin\&quot;, \&quot;proxy_admin_viewer\&quot;, \&quot;internal_user\&quot;, \&quot;internal_user_viewer\&quot;, \&quot;team\&quot;, \&quot;customer\&quot;. Info about each role here: &#x60;https://github.com/BerriAI/litellm/litellm/proxy/_types.py#L20&#x60; - max_budget: Optional[float] - Specify max budget for a given user. - budget_duration: Optional[str] - Budget is reset at the end of specified duration. If not set, budget is never reset. You can set duration as seconds (\&quot;30s\&quot;), minutes (\&quot;30m\&quot;), hours (\&quot;30h\&quot;), days (\&quot;30d\&quot;), months (\&quot;1mo\&quot;). - models: Optional[list] - Model_name&#39;s a user is allowed to call. (if empty, key is allowed to call all models). Set to [&#39;no-default-models&#39;] to block all model access. Restricting user to only team-based model access. - tpm_limit: Optional[int] - Specify tpm limit for a given user (Tokens per minute) - rpm_limit: Optional[int] - Specify rpm limit for a given user (Requests per minute) - auto_create_key: bool - Default&#x3D;True. Flag used for returning a key as part of the /user/new response - aliases: Optional[dict] - Model aliases for the user - [Docs](https://litellm.vercel.app/docs/proxy/virtual_keys#model-aliases) - config: Optional[dict] - [DEPRECATED PARAM] User-specific config. - allowed_cache_controls: Optional[list] - List of allowed cache control values. Example - [\&quot;no-cache\&quot;, \&quot;no-store\&quot;]. See all values - https://docs.litellm.ai/docs/proxy/caching#turn-on--off-caching-per-request- - blocked: Optional[bool] - [Not Implemented Yet] Whether the user is blocked. - guardrails: Optional[List[str]] - [Not Implemented Yet] List of active guardrails for the user - permissions: Optional[dict] - [Not Implemented Yet] User-specific permissions, eg. turning off pii masking. - metadata: Optional[dict] - Metadata for user, store information for user. Example metadata &#x3D; {\&quot;team\&quot;: \&quot;core-infra\&quot;, \&quot;app\&quot;: \&quot;app2\&quot;, \&quot;email\&quot;: \&quot;ishaan@berri.ai\&quot; } - max_parallel_requests: Optional[int] - Rate limit a user based on the number of parallel requests. Raises 429 error, if user&#39;s parallel requests &gt; x. - soft_budget: Optional[float] - Get alerts when user crosses given budget, doesn&#39;t block requests. - model_max_budget: Optional[dict] - Model-specific max budget for user. [Docs](https://docs.litellm.ai/docs/proxy/users#add-model-specific-budgets-to-keys) - model_rpm_limit: Optional[float] - Model-specific rpm limit for user. [Docs](https://docs.litellm.ai/docs/proxy/users#add-model-specific-limits-to-keys) - model_tpm_limit: Optional[float] - Model-specific tpm limit for user. [Docs](https://docs.litellm.ai/docs/proxy/users#add-model-specific-limits-to-keys) - spend: Optional[float] - Amount spent by user. Default is 0. Will be updated by proxy whenever user is used. You can set duration as seconds (\&quot;30s\&quot;), minutes (\&quot;30m\&quot;), hours (\&quot;30h\&quot;), days (\&quot;30d\&quot;), months (\&quot;1mo\&quot;). - team_id: Optional[str] - [DEPRECATED PARAM] The team id of the user. Default is None.  - duration: Optional[str] - Duration for the key auto-created on &#x60;/user/new&#x60;. Default is None. - key_alias: Optional[str] - Alias for the key auto-created on &#x60;/user/new&#x60;. Default is None. - sso_user_id: Optional[str] - The id of the user in the SSO provider. - object_permission: Optional[LiteLLM_ObjectPermissionBase] - internal user-specific object permission. Example - {\&quot;vector_stores\&quot;: [\&quot;vector_store_1\&quot;, \&quot;vector_store_2\&quot;]}. IF null or {} then no object permission. Returns: - key: (str) The generated api key for the user - expires: (datetime) Datetime object for when key expires. - user_id: (str) Unique user id - used for tracking spend across multiple keys for same user id. - max_budget: (float|None) Max budget for given user.  Usage Example   &#x60;&#x60;&#x60;shell  curl -X POST \&quot;http://localhost:4000/user/new\&quot;      -H \&quot;Content-Type: application/json\&quot;      -H \&quot;Authorization: Bearer sk-1234\&quot;      -d &#39;{      \&quot;username\&quot;: \&quot;new_user\&quot;,      \&quot;email\&quot;: \&quot;new_user@example.com\&quot;  }&#39; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **NewUserRequest** | [**NewUserRequest**](../Models/NewUserRequest.md)|  | |

### Return type

[**NewUserResponse**](../Models/NewUserResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="userInfoUserInfoGet"></a>
# **userInfoUserInfoGet**
> oas_any_type_not_mapped userInfoUserInfoGet(user\_id)

User Info

    [10/07/2024] Note: To get all users (+pagination), use &#x60;/user/list&#x60; endpoint.   Use this to get user information. (user row + all user key info)  Example request &#x60;&#x60;&#x60; curl -X GET &#39;http://localhost:4000/user/info?user_id&#x3D;krrish7%40berri.ai&#39;     --header &#39;Authorization: Bearer sk-1234&#39; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **user\_id** | **String**| User ID in the request parameters | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="userUpdateUserUpdatePost"></a>
# **userUpdateUserUpdatePost**
> oas_any_type_not_mapped userUpdateUserUpdatePost(UpdateUserRequest)

User Update

    Example curl   &#x60;&#x60;&#x60; curl --location &#39;http://0.0.0.0:4000/user/update&#39;     --header &#39;Authorization: Bearer sk-1234&#39;     --header &#39;Content-Type: application/json&#39;     --data &#39;{     \&quot;user_id\&quot;: \&quot;test-litellm-user-4\&quot;,     \&quot;user_role\&quot;: \&quot;proxy_admin_viewer\&quot; }&#39; &#x60;&#x60;&#x60;  Parameters:     - user_id: Optional[str] - Specify a user id. If not set, a unique id will be generated.     - user_email: Optional[str] - Specify a user email.     - password: Optional[str] - Specify a user password.     - user_alias: Optional[str] - A descriptive name for you to know who this user id refers to.     - teams: Optional[list] - specify a list of team id&#39;s a user belongs to.     - send_invite_email: Optional[bool] - Specify if an invite email should be sent.     - user_role: Optional[str] - Specify a user role - \&quot;proxy_admin\&quot;, \&quot;proxy_admin_viewer\&quot;, \&quot;internal_user\&quot;, \&quot;internal_user_viewer\&quot;, \&quot;team\&quot;, \&quot;customer\&quot;. Info about each role here: &#x60;https://github.com/BerriAI/litellm/litellm/proxy/_types.py#L20&#x60;     - max_budget: Optional[float] - Specify max budget for a given user.     - budget_duration: Optional[str] - Budget is reset at the end of specified duration. If not set, budget is never reset. You can set duration as seconds (\&quot;30s\&quot;), minutes (\&quot;30m\&quot;), hours (\&quot;30h\&quot;), days (\&quot;30d\&quot;), months (\&quot;1mo\&quot;).     - models: Optional[list] - Model_name&#39;s a user is allowed to call. (if empty, key is allowed to call all models)     - tpm_limit: Optional[int] - Specify tpm limit for a given user (Tokens per minute)     - rpm_limit: Optional[int] - Specify rpm limit for a given user (Requests per minute)     - auto_create_key: bool - Default&#x3D;True. Flag used for returning a key as part of the /user/new response     - aliases: Optional[dict] - Model aliases for the user - [Docs](https://litellm.vercel.app/docs/proxy/virtual_keys#model-aliases)     - config: Optional[dict] - [DEPRECATED PARAM] User-specific config.     - allowed_cache_controls: Optional[list] - List of allowed cache control values. Example - [\&quot;no-cache\&quot;, \&quot;no-store\&quot;]. See all values - https://docs.litellm.ai/docs/proxy/caching#turn-on--off-caching-per-request-     - blocked: Optional[bool] - [Not Implemented Yet] Whether the user is blocked.     - guardrails: Optional[List[str]] - [Not Implemented Yet] List of active guardrails for the user     - permissions: Optional[dict] - [Not Implemented Yet] User-specific permissions, eg. turning off pii masking.     - metadata: Optional[dict] - Metadata for user, store information for user. Example metadata &#x3D; {\&quot;team\&quot;: \&quot;core-infra\&quot;, \&quot;app\&quot;: \&quot;app2\&quot;, \&quot;email\&quot;: \&quot;ishaan@berri.ai\&quot; }     - max_parallel_requests: Optional[int] - Rate limit a user based on the number of parallel requests. Raises 429 error, if user&#39;s parallel requests &gt; x.     - soft_budget: Optional[float] - Get alerts when user crosses given budget, doesn&#39;t block requests.     - model_max_budget: Optional[dict] - Model-specific max budget for user. [Docs](https://docs.litellm.ai/docs/proxy/users#add-model-specific-budgets-to-keys)     - model_rpm_limit: Optional[float] - Model-specific rpm limit for user. [Docs](https://docs.litellm.ai/docs/proxy/users#add-model-specific-limits-to-keys)     - model_tpm_limit: Optional[float] - Model-specific tpm limit for user. [Docs](https://docs.litellm.ai/docs/proxy/users#add-model-specific-limits-to-keys)     - spend: Optional[float] - Amount spent by user. Default is 0. Will be updated by proxy whenever user is used. You can set duration as seconds (\&quot;30s\&quot;), minutes (\&quot;30m\&quot;), hours (\&quot;30h\&quot;), days (\&quot;30d\&quot;), months (\&quot;1mo\&quot;).     - team_id: Optional[str] - [DEPRECATED PARAM] The team id of the user. Default is None.      - duration: Optional[str] - [NOT IMPLEMENTED].     - key_alias: Optional[str] - [NOT IMPLEMENTED].     - object_permission: Optional[LiteLLM_ObjectPermissionBase] - internal user-specific object permission. Example - {\&quot;vector_stores\&quot;: [\&quot;vector_store_1\&quot;, \&quot;vector_store_2\&quot;]}. IF null or {} then no object permission.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **UpdateUserRequest** | [**UpdateUserRequest**](../Models/UpdateUserRequest.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

