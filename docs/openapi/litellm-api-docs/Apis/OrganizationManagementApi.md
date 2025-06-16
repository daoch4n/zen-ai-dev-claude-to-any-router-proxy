# OrganizationManagementApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**deleteOrganizationOrganizationDeleteDelete**](OrganizationManagementApi.md#deleteOrganizationOrganizationDeleteDelete) | **DELETE** /organization/delete | Delete Organization |
| [**deprecatedInfoOrganizationOrganizationInfoPost**](OrganizationManagementApi.md#deprecatedInfoOrganizationOrganizationInfoPost) | **POST** /organization/info | Deprecated Info Organization |
| [**infoOrganizationOrganizationInfoGet**](OrganizationManagementApi.md#infoOrganizationOrganizationInfoGet) | **GET** /organization/info | Info Organization |
| [**listOrganizationOrganizationListGet**](OrganizationManagementApi.md#listOrganizationOrganizationListGet) | **GET** /organization/list | List Organization |
| [**newOrganizationOrganizationNewPost**](OrganizationManagementApi.md#newOrganizationOrganizationNewPost) | **POST** /organization/new | New Organization |
| [**organizationMemberAddOrganizationMemberAddPost**](OrganizationManagementApi.md#organizationMemberAddOrganizationMemberAddPost) | **POST** /organization/member_add | Organization Member Add |
| [**organizationMemberDeleteOrganizationMemberDeleteDelete**](OrganizationManagementApi.md#organizationMemberDeleteOrganizationMemberDeleteDelete) | **DELETE** /organization/member_delete | Organization Member Delete |
| [**organizationMemberUpdateOrganizationMemberUpdatePatch**](OrganizationManagementApi.md#organizationMemberUpdateOrganizationMemberUpdatePatch) | **PATCH** /organization/member_update | Organization Member Update |
| [**updateOrganizationOrganizationUpdatePatch**](OrganizationManagementApi.md#updateOrganizationOrganizationUpdatePatch) | **PATCH** /organization/update | Update Organization |


<a name="deleteOrganizationOrganizationDeleteDelete"></a>
# **deleteOrganizationOrganizationDeleteDelete**
> List deleteOrganizationOrganizationDeleteDelete(DeleteOrganizationRequest)

Delete Organization

    Delete an organization  # Parameters:  - organization_ids: List[str] - The organization ids to delete.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **DeleteOrganizationRequest** | [**DeleteOrganizationRequest**](../Models/DeleteOrganizationRequest.md)|  | |

### Return type

[**List**](../Models/LiteLLM_OrganizationTableWithMembers.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="deprecatedInfoOrganizationOrganizationInfoPost"></a>
# **deprecatedInfoOrganizationOrganizationInfoPost**
> oas_any_type_not_mapped deprecatedInfoOrganizationOrganizationInfoPost(OrganizationRequest)

Deprecated Info Organization

    DEPRECATED: Use GET /organization/info instead

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **OrganizationRequest** | [**OrganizationRequest**](../Models/OrganizationRequest.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="infoOrganizationOrganizationInfoGet"></a>
# **infoOrganizationOrganizationInfoGet**
> LiteLLM_OrganizationTableWithMembers infoOrganizationOrganizationInfoGet(organization\_id)

Info Organization

    Get the org specific information

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **organization\_id** | **String**|  | [default to null] |

### Return type

[**LiteLLM_OrganizationTableWithMembers**](../Models/LiteLLM_OrganizationTableWithMembers.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="listOrganizationOrganizationListGet"></a>
# **listOrganizationOrganizationListGet**
> List listOrganizationOrganizationListGet()

List Organization

    &#x60;&#x60;&#x60; curl --location --request GET &#39;http://0.0.0.0:4000/organization/list&#39;         --header &#39;Authorization: Bearer sk-1234&#39; &#x60;&#x60;&#x60;

### Parameters
This endpoint does not need any parameter.

### Return type

[**List**](../Models/LiteLLM_OrganizationTableWithMembers.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="newOrganizationOrganizationNewPost"></a>
# **newOrganizationOrganizationNewPost**
> NewOrganizationResponse newOrganizationOrganizationNewPost(NewOrganizationRequest)

New Organization

    Allow orgs to own teams  Set org level budgets + model access.  Only admins can create orgs.  # Parameters  - organization_alias: *str* - The name of the organization. - models: *List* - The models the organization has access to. - budget_id: *Optional[str]* - The id for a budget (tpm/rpm/max budget) for the organization. ### IF NO BUDGET ID - CREATE ONE WITH THESE PARAMS ### - max_budget: *Optional[float]* - Max budget for org - tpm_limit: *Optional[int]* - Max tpm limit for org - rpm_limit: *Optional[int]* - Max rpm limit for org - max_parallel_requests: *Optional[int]* - [Not Implemented Yet] Max parallel requests for org - soft_budget: *Optional[float]* - [Not Implemented Yet] Get a slack alert when this soft budget is reached. Don&#39;t block requests. - model_max_budget: *Optional[dict]* - Max budget for a specific model - budget_duration: *Optional[str]* - Frequency of reseting org budget - metadata: *Optional[dict]* - Metadata for organization, store information for organization. Example metadata - {\&quot;extra_info\&quot;: \&quot;some info\&quot;} - blocked: *bool* - Flag indicating if the org is blocked or not - will stop all calls from keys with this org_id. - tags: *Optional[List[str]]* - Tags for [tracking spend](https://litellm.vercel.app/docs/proxy/enterprise#tracking-spend-for-custom-tags) and/or doing [tag-based routing](https://litellm.vercel.app/docs/proxy/tag_routing). - organization_id: *Optional[str]* - The organization id of the team. Default is None. Create via &#x60;/organization/new&#x60;. - model_aliases: Optional[dict] - Model aliases for the team. [Docs](https://docs.litellm.ai/docs/proxy/team_based_routing#create-team-with-model-alias) - object_permission: Optional[LiteLLM_ObjectPermissionBase] - organization-specific object permission. Example - {\&quot;vector_stores\&quot;: [\&quot;vector_store_1\&quot;, \&quot;vector_store_2\&quot;]}. IF null or {} then no object permission. Case 1: Create new org **without** a budget_id  &#x60;&#x60;&#x60;bash curl --location &#39;http://0.0.0.0:4000/organization/new&#39;  --header &#39;Authorization: Bearer sk-1234&#39;  --header &#39;Content-Type: application/json&#39;  --data &#39;{     \&quot;organization_alias\&quot;: \&quot;my-secret-org\&quot;,     \&quot;models\&quot;: [\&quot;model1\&quot;, \&quot;model2\&quot;],     \&quot;max_budget\&quot;: 100 }&#39;   &#x60;&#x60;&#x60;  Case 2: Create new org **with** a budget_id  &#x60;&#x60;&#x60;bash curl --location &#39;http://0.0.0.0:4000/organization/new&#39;  --header &#39;Authorization: Bearer sk-1234&#39;  --header &#39;Content-Type: application/json&#39;  --data &#39;{     \&quot;organization_alias\&quot;: \&quot;my-secret-org\&quot;,     \&quot;models\&quot;: [\&quot;model1\&quot;, \&quot;model2\&quot;],     \&quot;budget_id\&quot;: \&quot;428eeaa8-f3ac-4e85-a8fb-7dc8d7aa8689\&quot; }&#39; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **NewOrganizationRequest** | [**NewOrganizationRequest**](../Models/NewOrganizationRequest.md)|  | |

### Return type

[**NewOrganizationResponse**](../Models/NewOrganizationResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="organizationMemberAddOrganizationMemberAddPost"></a>
# **organizationMemberAddOrganizationMemberAddPost**
> OrganizationAddMemberResponse organizationMemberAddOrganizationMemberAddPost(OrganizationMemberAddRequest)

Organization Member Add

    [BETA]  Add new members (either via user_email or user_id) to an organization  If user doesn&#39;t exist, new user row will also be added to User Table  Only proxy_admin or org_admin of organization, allowed to access this endpoint.  # Parameters:  - organization_id: str (required) - member: Union[List[Member], Member] (required)     - role: Literal[LitellmUserRoles] (required)     - user_id: Optional[str]     - user_email: Optional[str]  Note: Either user_id or user_email must be provided for each member.  Example: &#x60;&#x60;&#x60; curl -X POST &#39;http://0.0.0.0:4000/organization/member_add&#39;     -H &#39;Authorization: Bearer sk-1234&#39;     -H &#39;Content-Type: application/json&#39;     -d &#39;{     \&quot;organization_id\&quot;: \&quot;45e3e396-ee08-4a61-a88e-16b3ce7e0849\&quot;,     \&quot;member\&quot;: {         \&quot;role\&quot;: \&quot;internal_user\&quot;,         \&quot;user_id\&quot;: \&quot;krrish247652@berri.ai\&quot;     },     \&quot;max_budget_in_organization\&quot;: 100.0 }&#39; &#x60;&#x60;&#x60;  The following is executed in this function:  1. Check if organization exists 2. Creates a new Internal User if the user_id or user_email is not found in LiteLLM_UserTable 3. Add Internal User to the &#x60;LiteLLM_OrganizationMembership&#x60; table

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **OrganizationMemberAddRequest** | [**OrganizationMemberAddRequest**](../Models/OrganizationMemberAddRequest.md)|  | |

### Return type

[**OrganizationAddMemberResponse**](../Models/OrganizationAddMemberResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="organizationMemberDeleteOrganizationMemberDeleteDelete"></a>
# **organizationMemberDeleteOrganizationMemberDeleteDelete**
> oas_any_type_not_mapped organizationMemberDeleteOrganizationMemberDeleteDelete(OrganizationMemberDeleteRequest)

Organization Member Delete

    Delete a member from an organization

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **OrganizationMemberDeleteRequest** | [**OrganizationMemberDeleteRequest**](../Models/OrganizationMemberDeleteRequest.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="organizationMemberUpdateOrganizationMemberUpdatePatch"></a>
# **organizationMemberUpdateOrganizationMemberUpdatePatch**
> LiteLLM_OrganizationMembershipTable organizationMemberUpdateOrganizationMemberUpdatePatch(OrganizationMemberUpdateRequest)

Organization Member Update

    Update a member&#39;s role in an organization

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **OrganizationMemberUpdateRequest** | [**OrganizationMemberUpdateRequest**](../Models/OrganizationMemberUpdateRequest.md)|  | |

### Return type

[**LiteLLM_OrganizationMembershipTable**](../Models/LiteLLM_OrganizationMembershipTable.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="updateOrganizationOrganizationUpdatePatch"></a>
# **updateOrganizationOrganizationUpdatePatch**
> LiteLLM_OrganizationTableWithMembers updateOrganizationOrganizationUpdatePatch(LiteLLM\_OrganizationTableUpdate)

Update Organization

    Update an organization

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **LiteLLM\_OrganizationTableUpdate** | [**LiteLLM_OrganizationTableUpdate**](../Models/LiteLLM_OrganizationTableUpdate.md)|  | |

### Return type

[**LiteLLM_OrganizationTableWithMembers**](../Models/LiteLLM_OrganizationTableWithMembers.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

