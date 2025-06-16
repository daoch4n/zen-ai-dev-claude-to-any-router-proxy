# TeamManagementApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**addTeamCallbacksTeamTeamIdCallbackPost**](TeamManagementApi.md#addTeamCallbacksTeamTeamIdCallbackPost) | **POST** /team/{team_id}/callback | Add Team Callbacks |
| [**blockTeamTeamBlockPost**](TeamManagementApi.md#blockTeamTeamBlockPost) | **POST** /team/block | Block Team |
| [**deleteTeamTeamDeletePost**](TeamManagementApi.md#deleteTeamTeamDeletePost) | **POST** /team/delete | Delete Team |
| [**disableTeamLoggingTeamTeamIdDisableLoggingPost**](TeamManagementApi.md#disableTeamLoggingTeamTeamIdDisableLoggingPost) | **POST** /team/{team_id}/disable_logging | Disable Team Logging |
| [**getTeamCallbacksTeamTeamIdCallbackGet**](TeamManagementApi.md#getTeamCallbacksTeamTeamIdCallbackGet) | **GET** /team/{team_id}/callback | Get Team Callbacks |
| [**getTeamDailyActivityTeamDailyActivityGet**](TeamManagementApi.md#getTeamDailyActivityTeamDailyActivityGet) | **GET** /team/daily/activity | Get Team Daily Activity |
| [**listTeamTeamListGet**](TeamManagementApi.md#listTeamTeamListGet) | **GET** /team/list | List Team |
| [**listTeamV2V2TeamListGet**](TeamManagementApi.md#listTeamV2V2TeamListGet) | **GET** /v2/team/list | List Team V2 |
| [**newTeamTeamNewPost**](TeamManagementApi.md#newTeamTeamNewPost) | **POST** /team/new | New Team |
| [**teamInfoTeamInfoGet**](TeamManagementApi.md#teamInfoTeamInfoGet) | **GET** /team/info | Team Info |
| [**teamMemberAddTeamMemberAddPost**](TeamManagementApi.md#teamMemberAddTeamMemberAddPost) | **POST** /team/member_add | Team Member Add |
| [**teamMemberDeleteTeamMemberDeletePost**](TeamManagementApi.md#teamMemberDeleteTeamMemberDeletePost) | **POST** /team/member_delete | Team Member Delete |
| [**teamMemberPermissionsTeamPermissionsListGet**](TeamManagementApi.md#teamMemberPermissionsTeamPermissionsListGet) | **GET** /team/permissions_list | Team Member Permissions |
| [**teamMemberUpdateTeamMemberUpdatePost**](TeamManagementApi.md#teamMemberUpdateTeamMemberUpdatePost) | **POST** /team/member_update | Team Member Update |
| [**teamModelAddTeamModelAddPost**](TeamManagementApi.md#teamModelAddTeamModelAddPost) | **POST** /team/model/add | Team Model Add |
| [**teamModelDeleteTeamModelDeletePost**](TeamManagementApi.md#teamModelDeleteTeamModelDeletePost) | **POST** /team/model/delete | Team Model Delete |
| [**unblockTeamTeamUnblockPost**](TeamManagementApi.md#unblockTeamTeamUnblockPost) | **POST** /team/unblock | Unblock Team |
| [**updateTeamMemberPermissionsTeamPermissionsUpdatePost**](TeamManagementApi.md#updateTeamMemberPermissionsTeamPermissionsUpdatePost) | **POST** /team/permissions_update | Update Team Member Permissions |
| [**updateTeamTeamUpdatePost**](TeamManagementApi.md#updateTeamTeamUpdatePost) | **POST** /team/update | Update Team |


<a name="addTeamCallbacksTeamTeamIdCallbackPost"></a>
# **addTeamCallbacksTeamTeamIdCallbackPost**
> oas_any_type_not_mapped addTeamCallbacksTeamTeamIdCallbackPost(team\_id, AddTeamCallback, litellm-changed-by)

Add Team Callbacks

    Add a success/failure callback to a team  Use this if if you want different teams to have different success/failure callbacks  Parameters: - callback_name (Literal[\&quot;langfuse\&quot;, \&quot;langsmith\&quot;, \&quot;gcs\&quot;], required): The name of the callback to add - callback_type (Literal[\&quot;success\&quot;, \&quot;failure\&quot;, \&quot;success_and_failure\&quot;], required): The type of callback to add. One of:     - \&quot;success\&quot;: Callback for successful LLM calls     - \&quot;failure\&quot;: Callback for failed LLM calls     - \&quot;success_and_failure\&quot;: Callback for both successful and failed LLM calls - callback_vars (StandardCallbackDynamicParams, required): A dictionary of variables to pass to the callback     - langfuse_public_key: The public key for the Langfuse callback     - langfuse_secret_key: The secret key for the Langfuse callback     - langfuse_secret: The secret for the Langfuse callback     - langfuse_host: The host for the Langfuse callback     - gcs_bucket_name: The name of the GCS bucket     - gcs_path_service_account: The path to the GCS service account     - langsmith_api_key: The API key for the Langsmith callback     - langsmith_project: The project for the Langsmith callback     - langsmith_base_url: The base URL for the Langsmith callback  Example curl: &#x60;&#x60;&#x60; curl -X POST &#39;http:/localhost:4000/team/dbe2f686-a686-4896-864a-4c3924458709/callback&#39;         -H &#39;Content-Type: application/json&#39;         -H &#39;Authorization: Bearer sk-1234&#39;         -d &#39;{     \&quot;callback_name\&quot;: \&quot;langfuse\&quot;,     \&quot;callback_type\&quot;: \&quot;success\&quot;,     \&quot;callback_vars\&quot;: {\&quot;langfuse_public_key\&quot;: \&quot;pk-lf-xxxx1\&quot;, \&quot;langfuse_secret_key\&quot;: \&quot;sk-xxxxx\&quot;}      }&#39; &#x60;&#x60;&#x60;  This means for the team where team_id &#x3D; dbe2f686-a686-4896-864a-4c3924458709, all LLM calls will be logged to langfuse using the public key pk-lf-xxxx1 and the secret key sk-xxxxx

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **team\_id** | **String**|  | [default to null] |
| **AddTeamCallback** | [**AddTeamCallback**](../Models/AddTeamCallback.md)|  | |
| **litellm-changed-by** | **String**| The litellm-changed-by header enables tracking of actions performed by authorized users on behalf of other users, providing an audit trail for accountability | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="blockTeamTeamBlockPost"></a>
# **blockTeamTeamBlockPost**
> oas_any_type_not_mapped blockTeamTeamBlockPost(BlockTeamRequest)

Block Team

    Blocks all calls from keys with this team id.  Parameters: - team_id: str - Required. The unique identifier of the team to block.  Example: &#x60;&#x60;&#x60; curl --location &#39;http://0.0.0.0:4000/team/block&#39;     --header &#39;Authorization: Bearer sk-1234&#39;     --header &#39;Content-Type: application/json&#39;     --data &#39;{     \&quot;team_id\&quot;: \&quot;team-1234\&quot; }&#39; &#x60;&#x60;&#x60;  Returns: - The updated team record with blocked&#x3D;True

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **BlockTeamRequest** | [**BlockTeamRequest**](../Models/BlockTeamRequest.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="deleteTeamTeamDeletePost"></a>
# **deleteTeamTeamDeletePost**
> oas_any_type_not_mapped deleteTeamTeamDeletePost(DeleteTeamRequest, litellm-changed-by)

Delete Team

    delete team and associated team keys  Parameters: - team_ids: List[str] - Required. List of team IDs to delete. Example: [\&quot;team-1234\&quot;, \&quot;team-5678\&quot;]  &#x60;&#x60;&#x60; curl --location &#39;http://0.0.0.0:4000/team/delete&#39;     --header &#39;Authorization: Bearer sk-1234&#39;     --header &#39;Content-Type: application/json&#39;     --data-raw &#39;{     \&quot;team_ids\&quot;: [\&quot;8d916b1c-510d-4894-a334-1c16a93344f5\&quot;] }&#39; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **DeleteTeamRequest** | [**DeleteTeamRequest**](../Models/DeleteTeamRequest.md)|  | |
| **litellm-changed-by** | **String**| The litellm-changed-by header enables tracking of actions performed by authorized users on behalf of other users, providing an audit trail for accountability | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="disableTeamLoggingTeamTeamIdDisableLoggingPost"></a>
# **disableTeamLoggingTeamTeamIdDisableLoggingPost**
> oas_any_type_not_mapped disableTeamLoggingTeamTeamIdDisableLoggingPost(team\_id)

Disable Team Logging

    Disable all logging callbacks for a team  Parameters: - team_id (str, required): The unique identifier for the team  Example curl: &#x60;&#x60;&#x60; curl -X POST &#39;http://localhost:4000/team/dbe2f686-a686-4896-864a-4c3924458709/disable_logging&#39;         -H &#39;Authorization: Bearer sk-1234&#39; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **team\_id** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getTeamCallbacksTeamTeamIdCallbackGet"></a>
# **getTeamCallbacksTeamTeamIdCallbackGet**
> oas_any_type_not_mapped getTeamCallbacksTeamTeamIdCallbackGet(team\_id)

Get Team Callbacks

    Get the success/failure callbacks and variables for a team  Parameters: - team_id (str, required): The unique identifier for the team  Example curl: &#x60;&#x60;&#x60; curl -X GET &#39;http://localhost:4000/team/dbe2f686-a686-4896-864a-4c3924458709/callback&#39;         -H &#39;Authorization: Bearer sk-1234&#39; &#x60;&#x60;&#x60;  This will return the callback settings for the team with id dbe2f686-a686-4896-864a-4c3924458709  Returns {         \&quot;status\&quot;: \&quot;success\&quot;,         \&quot;data\&quot;: {             \&quot;team_id\&quot;: team_id,             \&quot;success_callbacks\&quot;: team_callback_settings_obj.success_callback,             \&quot;failure_callbacks\&quot;: team_callback_settings_obj.failure_callback,             \&quot;callback_vars\&quot;: team_callback_settings_obj.callback_vars,         },     }

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **team\_id** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getTeamDailyActivityTeamDailyActivityGet"></a>
# **getTeamDailyActivityTeamDailyActivityGet**
> SpendAnalyticsPaginatedResponse getTeamDailyActivityTeamDailyActivityGet(team\_ids, start\_date, end\_date, model, api\_key, page, page\_size, exclude\_team\_ids)

Get Team Daily Activity

    Get daily activity for specific teams or all teams.  Args:     team_ids (Optional[str]): Comma-separated list of team IDs to filter by. If not provided, returns data for all teams.     start_date (Optional[str]): Start date for the activity period (YYYY-MM-DD).     end_date (Optional[str]): End date for the activity period (YYYY-MM-DD).     model (Optional[str]): Filter by model name.     api_key (Optional[str]): Filter by API key.     page (int): Page number for pagination.     page_size (int): Number of items per page.     exclude_team_ids (Optional[str]): Comma-separated list of team IDs to exclude. Returns:     SpendAnalyticsPaginatedResponse: Paginated response containing daily activity data.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **team\_ids** | **String**|  | [optional] [default to null] |
| **start\_date** | **String**|  | [optional] [default to null] |
| **end\_date** | **String**|  | [optional] [default to null] |
| **model** | **String**|  | [optional] [default to null] |
| **api\_key** | **String**|  | [optional] [default to null] |
| **page** | **Integer**|  | [optional] [default to 1] |
| **page\_size** | **Integer**|  | [optional] [default to 10] |
| **exclude\_team\_ids** | **String**|  | [optional] [default to null] |

### Return type

[**SpendAnalyticsPaginatedResponse**](../Models/SpendAnalyticsPaginatedResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="listTeamTeamListGet"></a>
# **listTeamTeamListGet**
> oas_any_type_not_mapped listTeamTeamListGet(user\_id, organization\_id)

List Team

    &#x60;&#x60;&#x60; curl --location --request GET &#39;http://0.0.0.0:4000/team/list&#39;         --header &#39;Authorization: Bearer sk-1234&#39; &#x60;&#x60;&#x60;  Parameters: - user_id: str - Optional. If passed will only return teams that the user_id is a member of. - organization_id: str - Optional. If passed will only return teams that belong to the organization_id. Pass &#39;default_organization&#39; to get all teams without organization_id.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **user\_id** | **String**| Only return teams which this &#39;user_id&#39; belongs to | [optional] [default to null] |
| **organization\_id** | **String**|  | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="listTeamV2V2TeamListGet"></a>
# **listTeamV2V2TeamListGet**
> TeamListResponse listTeamV2V2TeamListGet(user\_id, organization\_id, team\_id, team\_alias, page, page\_size, sort\_by, sort\_order)

List Team V2

    Get a paginated list of teams with filtering and sorting options.  Parameters:     user_id: Optional[str]         Only return teams which this user belongs to     organization_id: Optional[str]         Only return teams which belong to this organization     team_id: Optional[str]         Filter teams by exact team_id match     team_alias: Optional[str]         Filter teams by partial team_alias match     page: int         The page number to return     page_size: int         The number of items per page     sort_by: Optional[str]         Column to sort by (e.g. &#39;team_id&#39;, &#39;team_alias&#39;, &#39;created_at&#39;)     sort_order: str         Sort order (&#39;asc&#39; or &#39;desc&#39;)

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **user\_id** | **String**| Only return teams which this &#39;user_id&#39; belongs to | [optional] [default to null] |
| **organization\_id** | **String**| Only return teams which this &#39;organization_id&#39; belongs to | [optional] [default to null] |
| **team\_id** | **String**| Only return teams which this &#39;team_id&#39; belongs to | [optional] [default to null] |
| **team\_alias** | **String**| Only return teams which this &#39;team_alias&#39; belongs to. Supports partial matching. | [optional] [default to null] |
| **page** | **Integer**| Page number for pagination | [optional] [default to 1] |
| **page\_size** | **Integer**| Number of teams per page | [optional] [default to 10] |
| **sort\_by** | **String**| Column to sort by (e.g. &#39;team_id&#39;, &#39;team_alias&#39;, &#39;created_at&#39;) | [optional] [default to null] |
| **sort\_order** | **String**| Sort order (&#39;asc&#39; or &#39;desc&#39;) | [optional] [default to asc] |

### Return type

[**TeamListResponse**](../Models/TeamListResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="newTeamTeamNewPost"></a>
# **newTeamTeamNewPost**
> LiteLLM_TeamTable newTeamTeamNewPost(NewTeamRequest, litellm-changed-by)

New Team

    Allow users to create a new team. Apply user permissions to their team.  👉 [Detailed Doc on setting team budgets](https://docs.litellm.ai/docs/proxy/team_budgets)   Parameters: - team_alias: Optional[str] - User defined team alias - team_id: Optional[str] - The team id of the user. If none passed, we&#39;ll generate it. - members_with_roles: List[{\&quot;role\&quot;: \&quot;admin\&quot; or \&quot;user\&quot;, \&quot;user_id\&quot;: \&quot;&lt;user-id&gt;\&quot;}] - A list of users and their roles in the team. Get user_id when making a new user via &#x60;/user/new&#x60;. - team_member_permissions: Optional[List[str]] - A list of routes that non-admin team members can access. example: [\&quot;/key/generate\&quot;, \&quot;/key/update\&quot;, \&quot;/key/delete\&quot;] - metadata: Optional[dict] - Metadata for team, store information for team. Example metadata &#x3D; {\&quot;extra_info\&quot;: \&quot;some info\&quot;} - tpm_limit: Optional[int] - The TPM (Tokens Per Minute) limit for this team - all keys with this team_id will have at max this TPM limit - rpm_limit: Optional[int] - The RPM (Requests Per Minute) limit for this team - all keys associated with this team_id will have at max this RPM limit - max_budget: Optional[float] - The maximum budget allocated to the team - all keys for this team_id will have at max this max_budget - budget_duration: Optional[str] - The duration of the budget for the team. Doc [here](https://docs.litellm.ai/docs/proxy/team_budgets) - models: Optional[list] - A list of models associated with the team - all keys for this team_id will have at most, these models. If empty, assumes all models are allowed. - blocked: bool - Flag indicating if the team is blocked or not - will stop all calls from keys with this team_id. - members: Optional[List] - Control team members via &#x60;/team/member/add&#x60; and &#x60;/team/member/delete&#x60;. - tags: Optional[List[str]] - Tags for [tracking spend](https://litellm.vercel.app/docs/proxy/enterprise#tracking-spend-for-custom-tags) and/or doing [tag-based routing](https://litellm.vercel.app/docs/proxy/tag_routing). - organization_id: Optional[str] - The organization id of the team. Default is None. Create via &#x60;/organization/new&#x60;. - model_aliases: Optional[dict] - Model aliases for the team. [Docs](https://docs.litellm.ai/docs/proxy/team_based_routing#create-team-with-model-alias) - guardrails: Optional[List[str]] - Guardrails for the team. [Docs](https://docs.litellm.ai/docs/proxy/guardrails) - object_permission: Optional[LiteLLM_ObjectPermissionBase] - team-specific object permission. Example - {\&quot;vector_stores\&quot;: [\&quot;vector_store_1\&quot;, \&quot;vector_store_2\&quot;]}. IF null or {} then no object permission.  Returns: - team_id: (str) Unique team id - used for tracking spend across multiple keys for same team id.  _deprecated_params: - admins: list - A list of user_id&#39;s for the admin role - users: list - A list of user_id&#39;s for the user role  Example Request: &#x60;&#x60;&#x60; curl --location &#39;http://0.0.0.0:4000/team/new&#39;     --header &#39;Authorization: Bearer sk-1234&#39;     --header &#39;Content-Type: application/json&#39;     --data &#39;{   \&quot;team_alias\&quot;: \&quot;my-new-team_2\&quot;,   \&quot;members_with_roles\&quot;: [{\&quot;role\&quot;: \&quot;admin\&quot;, \&quot;user_id\&quot;: \&quot;user-1234\&quot;},     {\&quot;role\&quot;: \&quot;user\&quot;, \&quot;user_id\&quot;: \&quot;user-2434\&quot;}] }&#39;  &#x60;&#x60;&#x60;   &#x60;&#x60;&#x60; curl --location &#39;http://0.0.0.0:4000/team/new&#39;     --header &#39;Authorization: Bearer sk-1234&#39;     --header &#39;Content-Type: application/json&#39;     --data &#39;{             \&quot;team_alias\&quot;: \&quot;QA Prod Bot\&quot;,             \&quot;max_budget\&quot;: 0.000000001,             \&quot;budget_duration\&quot;: \&quot;1d\&quot;         }&#39; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **NewTeamRequest** | [**NewTeamRequest**](../Models/NewTeamRequest.md)|  | |
| **litellm-changed-by** | **String**| The litellm-changed-by header enables tracking of actions performed by authorized users on behalf of other users, providing an audit trail for accountability | [optional] [default to null] |

### Return type

[**LiteLLM_TeamTable**](../Models/LiteLLM_TeamTable.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="teamInfoTeamInfoGet"></a>
# **teamInfoTeamInfoGet**
> oas_any_type_not_mapped teamInfoTeamInfoGet(team\_id)

Team Info

    get info on team + related keys  Parameters: - team_id: str - Required. The unique identifier of the team to get info on.  &#x60;&#x60;&#x60; curl --location &#39;http://localhost:4000/team/info?team_id&#x3D;your_team_id_here&#39;     --header &#39;Authorization: Bearer your_api_key_here&#39; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **team\_id** | **String**| Team ID in the request parameters | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="teamMemberAddTeamMemberAddPost"></a>
# **teamMemberAddTeamMemberAddPost**
> TeamAddMemberResponse teamMemberAddTeamMemberAddPost(TeamMemberAddRequest)

Team Member Add

    [BETA]  Add new members (either via user_email or user_id) to a team  If user doesn&#39;t exist, new user row will also be added to User Table  Only proxy_admin or admin of team, allowed to access this endpoint. &#x60;&#x60;&#x60;  curl -X POST &#39;http://0.0.0.0:4000/team/member_add&#39;     -H &#39;Authorization: Bearer sk-1234&#39;     -H &#39;Content-Type: application/json&#39;     -d &#39;{\&quot;team_id\&quot;: \&quot;45e3e396-ee08-4a61-a88e-16b3ce7e0849\&quot;, \&quot;member\&quot;: {\&quot;role\&quot;: \&quot;user\&quot;, \&quot;user_id\&quot;: \&quot;krrish247652@berri.ai\&quot;}}&#39;  &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **TeamMemberAddRequest** | [**TeamMemberAddRequest**](../Models/TeamMemberAddRequest.md)|  | |

### Return type

[**TeamAddMemberResponse**](../Models/TeamAddMemberResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="teamMemberDeleteTeamMemberDeletePost"></a>
# **teamMemberDeleteTeamMemberDeletePost**
> oas_any_type_not_mapped teamMemberDeleteTeamMemberDeletePost(TeamMemberDeleteRequest)

Team Member Delete

    [BETA]  delete members (either via user_email or user_id) from a team  If user doesn&#39;t exist, an exception will be raised &#x60;&#x60;&#x60; curl -X POST &#39;http://0.0.0.0:8000/team/member_delete&#39;  -H &#39;Authorization: Bearer sk-1234&#39;  -H &#39;Content-Type: application/json&#39;  -d &#39;{     \&quot;team_id\&quot;: \&quot;45e3e396-ee08-4a61-a88e-16b3ce7e0849\&quot;,     \&quot;user_id\&quot;: \&quot;krrish247652@berri.ai\&quot; }&#39; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **TeamMemberDeleteRequest** | [**TeamMemberDeleteRequest**](../Models/TeamMemberDeleteRequest.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="teamMemberPermissionsTeamPermissionsListGet"></a>
# **teamMemberPermissionsTeamPermissionsListGet**
> GetTeamMemberPermissionsResponse teamMemberPermissionsTeamPermissionsListGet(team\_id)

Team Member Permissions

    Get the team member permissions for a team

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **team\_id** | **String**| Team ID in the request parameters | [optional] [default to null] |

### Return type

[**GetTeamMemberPermissionsResponse**](../Models/GetTeamMemberPermissionsResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="teamMemberUpdateTeamMemberUpdatePost"></a>
# **teamMemberUpdateTeamMemberUpdatePost**
> TeamMemberUpdateResponse teamMemberUpdateTeamMemberUpdatePost(TeamMemberUpdateRequest)

Team Member Update

    [BETA]  Update team member budgets and team member role

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **TeamMemberUpdateRequest** | [**TeamMemberUpdateRequest**](../Models/TeamMemberUpdateRequest.md)|  | |

### Return type

[**TeamMemberUpdateResponse**](../Models/TeamMemberUpdateResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="teamModelAddTeamModelAddPost"></a>
# **teamModelAddTeamModelAddPost**
> oas_any_type_not_mapped teamModelAddTeamModelAddPost(TeamModelAddRequest)

Team Model Add

    Add models to a team&#39;s allowed model list. Only proxy admin or team admin can add models.  Parameters: - team_id: str - Required. The team to add models to - models: List[str] - Required. List of models to add to the team  Example Request: &#x60;&#x60;&#x60; curl --location &#39;http://0.0.0.0:4000/team/model/add&#39;     --header &#39;Authorization: Bearer sk-1234&#39;     --header &#39;Content-Type: application/json&#39;     --data &#39;{     \&quot;team_id\&quot;: \&quot;team-1234\&quot;,     \&quot;models\&quot;: [\&quot;gpt-4\&quot;, \&quot;claude-2\&quot;] }&#39; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **TeamModelAddRequest** | [**TeamModelAddRequest**](../Models/TeamModelAddRequest.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="teamModelDeleteTeamModelDeletePost"></a>
# **teamModelDeleteTeamModelDeletePost**
> oas_any_type_not_mapped teamModelDeleteTeamModelDeletePost(TeamModelDeleteRequest)

Team Model Delete

    Remove models from a team&#39;s allowed model list. Only proxy admin or team admin can remove models.  Parameters: - team_id: str - Required. The team to remove models from - models: List[str] - Required. List of models to remove from the team  Example Request: &#x60;&#x60;&#x60; curl --location &#39;http://0.0.0.0:4000/team/model/delete&#39;     --header &#39;Authorization: Bearer sk-1234&#39;     --header &#39;Content-Type: application/json&#39;     --data &#39;{     \&quot;team_id\&quot;: \&quot;team-1234\&quot;,     \&quot;models\&quot;: [\&quot;gpt-4\&quot;] }&#39; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **TeamModelDeleteRequest** | [**TeamModelDeleteRequest**](../Models/TeamModelDeleteRequest.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="unblockTeamTeamUnblockPost"></a>
# **unblockTeamTeamUnblockPost**
> oas_any_type_not_mapped unblockTeamTeamUnblockPost(BlockTeamRequest)

Unblock Team

    Blocks all calls from keys with this team id.  Parameters: - team_id: str - Required. The unique identifier of the team to unblock.  Example: &#x60;&#x60;&#x60; curl --location &#39;http://0.0.0.0:4000/team/unblock&#39;     --header &#39;Authorization: Bearer sk-1234&#39;     --header &#39;Content-Type: application/json&#39;     --data &#39;{     \&quot;team_id\&quot;: \&quot;team-1234\&quot; }&#39; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **BlockTeamRequest** | [**BlockTeamRequest**](../Models/BlockTeamRequest.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="updateTeamMemberPermissionsTeamPermissionsUpdatePost"></a>
# **updateTeamMemberPermissionsTeamPermissionsUpdatePost**
> LiteLLM_TeamTable updateTeamMemberPermissionsTeamPermissionsUpdatePost(UpdateTeamMemberPermissionsRequest)

Update Team Member Permissions

    Update the team member permissions for a team

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **UpdateTeamMemberPermissionsRequest** | [**UpdateTeamMemberPermissionsRequest**](../Models/UpdateTeamMemberPermissionsRequest.md)|  | |

### Return type

[**LiteLLM_TeamTable**](../Models/LiteLLM_TeamTable.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="updateTeamTeamUpdatePost"></a>
# **updateTeamTeamUpdatePost**
> oas_any_type_not_mapped updateTeamTeamUpdatePost(UpdateTeamRequest, litellm-changed-by)

Update Team

    Use &#x60;/team/member_add&#x60; AND &#x60;/team/member/delete&#x60; to add/remove new team members  You can now update team budget / rate limits via /team/update  Parameters: - team_id: str - The team id of the user. Required param. - team_alias: Optional[str] - User defined team alias - team_member_permissions: Optional[List[str]] - A list of routes that non-admin team members can access. example: [\&quot;/key/generate\&quot;, \&quot;/key/update\&quot;, \&quot;/key/delete\&quot;] - metadata: Optional[dict] - Metadata for team, store information for team. Example metadata &#x3D; {\&quot;team\&quot;: \&quot;core-infra\&quot;, \&quot;app\&quot;: \&quot;app2\&quot;, \&quot;email\&quot;: \&quot;ishaan@berri.ai\&quot; } - tpm_limit: Optional[int] - The TPM (Tokens Per Minute) limit for this team - all keys with this team_id will have at max this TPM limit - rpm_limit: Optional[int] - The RPM (Requests Per Minute) limit for this team - all keys associated with this team_id will have at max this RPM limit - max_budget: Optional[float] - The maximum budget allocated to the team - all keys for this team_id will have at max this max_budget - budget_duration: Optional[str] - The duration of the budget for the team. Doc [here](https://docs.litellm.ai/docs/proxy/team_budgets) - models: Optional[list] - A list of models associated with the team - all keys for this team_id will have at most, these models. If empty, assumes all models are allowed. - blocked: bool - Flag indicating if the team is blocked or not - will stop all calls from keys with this team_id. - tags: Optional[List[str]] - Tags for [tracking spend](https://litellm.vercel.app/docs/proxy/enterprise#tracking-spend-for-custom-tags) and/or doing [tag-based routing](https://litellm.vercel.app/docs/proxy/tag_routing). - organization_id: Optional[str] - The organization id of the team. Default is None. Create via &#x60;/organization/new&#x60;. - model_aliases: Optional[dict] - Model aliases for the team. [Docs](https://docs.litellm.ai/docs/proxy/team_based_routing#create-team-with-model-alias) - guardrails: Optional[List[str]] - Guardrails for the team. [Docs](https://docs.litellm.ai/docs/proxy/guardrails) - object_permission: Optional[LiteLLM_ObjectPermissionBase] - team-specific object permission. Example - {\&quot;vector_stores\&quot;: [\&quot;vector_store_1\&quot;, \&quot;vector_store_2\&quot;]}. IF null or {} then no object permission. Example - update team TPM Limit  &#x60;&#x60;&#x60; curl --location &#39;http://0.0.0.0:4000/team/update&#39;     --header &#39;Authorization: Bearer sk-1234&#39;     --header &#39;Content-Type: application/json&#39;     --data-raw &#39;{     \&quot;team_id\&quot;: \&quot;8d916b1c-510d-4894-a334-1c16a93344f5\&quot;,     \&quot;tpm_limit\&quot;: 100 }&#39; &#x60;&#x60;&#x60;  Example - Update Team &#x60;max_budget&#x60; budget &#x60;&#x60;&#x60; curl --location &#39;http://0.0.0.0:4000/team/update&#39;     --header &#39;Authorization: Bearer sk-1234&#39;     --header &#39;Content-Type: application/json&#39;     --data-raw &#39;{     \&quot;team_id\&quot;: \&quot;8d916b1c-510d-4894-a334-1c16a93344f5\&quot;,     \&quot;max_budget\&quot;: 10 }&#39; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **UpdateTeamRequest** | [**UpdateTeamRequest**](../Models/UpdateTeamRequest.md)|  | |
| **litellm-changed-by** | **String**| The litellm-changed-by header enables tracking of actions performed by authorized users on behalf of other users, providing an audit trail for accountability | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

