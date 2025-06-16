# CustomerManagementApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**blockUserCustomerBlockPost**](CustomerManagementApi.md#blockUserCustomerBlockPost) | **POST** /customer/block | Block User |
| [**deleteEndUserCustomerDeletePost**](CustomerManagementApi.md#deleteEndUserCustomerDeletePost) | **POST** /customer/delete | Delete End User |
| [**endUserInfoCustomerInfoGet**](CustomerManagementApi.md#endUserInfoCustomerInfoGet) | **GET** /customer/info | End User Info |
| [**listEndUserCustomerListGet**](CustomerManagementApi.md#listEndUserCustomerListGet) | **GET** /customer/list | List End User |
| [**newEndUserCustomerNewPost**](CustomerManagementApi.md#newEndUserCustomerNewPost) | **POST** /customer/new | New End User |
| [**unblockUserCustomerUnblockPost**](CustomerManagementApi.md#unblockUserCustomerUnblockPost) | **POST** /customer/unblock | Unblock User |
| [**updateEndUserCustomerUpdatePost**](CustomerManagementApi.md#updateEndUserCustomerUpdatePost) | **POST** /customer/update | Update End User |


<a name="blockUserCustomerBlockPost"></a>
# **blockUserCustomerBlockPost**
> oas_any_type_not_mapped blockUserCustomerBlockPost(BlockUsers)

Block User

    [BETA] Reject calls with this end-user id  Parameters: - user_ids (List[str], required): The unique &#x60;user_id&#x60;s for the users to block      (any /chat/completion call with this user&#x3D;{end-user-id} param, will be rejected.)      &#x60;&#x60;&#x60;     curl -X POST \&quot;http://0.0.0.0:8000/user/block\&quot;     -H \&quot;Authorization: Bearer sk-1234\&quot;     -d &#39;{     \&quot;user_ids\&quot;: [&lt;user_id&gt;, ...]     }&#39;     &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **BlockUsers** | [**BlockUsers**](../Models/BlockUsers.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="deleteEndUserCustomerDeletePost"></a>
# **deleteEndUserCustomerDeletePost**
> oas_any_type_not_mapped deleteEndUserCustomerDeletePost(DeleteCustomerRequest)

Delete End User

    Delete multiple end-users.  Parameters: - user_ids (List[str], required): The unique &#x60;user_id&#x60;s for the users to delete  Example curl: &#x60;&#x60;&#x60; curl --location &#39;http://0.0.0.0:4000/customer/delete&#39;         --header &#39;Authorization: Bearer sk-1234&#39;         --header &#39;Content-Type: application/json&#39;         --data &#39;{         \&quot;user_ids\&quot; :[\&quot;ishaan-jaff-5\&quot;] }&#39;  See below for all params  &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **DeleteCustomerRequest** | [**DeleteCustomerRequest**](../Models/DeleteCustomerRequest.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="endUserInfoCustomerInfoGet"></a>
# **endUserInfoCustomerInfoGet**
> LiteLLM_EndUserTable endUserInfoCustomerInfoGet(end\_user\_id)

End User Info

    Get information about an end-user. An &#x60;end_user&#x60; is a customer (external user) of the proxy.  Parameters: - end_user_id (str, required): The unique identifier for the end-user  Example curl: &#x60;&#x60;&#x60; curl -X GET &#39;http://localhost:4000/customer/info?end_user_id&#x3D;test-litellm-user-4&#39;         -H &#39;Authorization: Bearer sk-1234&#39; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **end\_user\_id** | **String**| End User ID in the request parameters | [default to null] |

### Return type

[**LiteLLM_EndUserTable**](../Models/LiteLLM_EndUserTable.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="listEndUserCustomerListGet"></a>
# **listEndUserCustomerListGet**
> List listEndUserCustomerListGet()

List End User

    [Admin-only] List all available customers  Example curl: &#x60;&#x60;&#x60; curl --location --request GET &#39;http://0.0.0.0:4000/customer/list&#39;         --header &#39;Authorization: Bearer sk-1234&#39; &#x60;&#x60;&#x60;

### Parameters
This endpoint does not need any parameter.

### Return type

[**List**](../Models/LiteLLM_EndUserTable.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="newEndUserCustomerNewPost"></a>
# **newEndUserCustomerNewPost**
> oas_any_type_not_mapped newEndUserCustomerNewPost(NewCustomerRequest)

New End User

    Allow creating a new Customer    Parameters: - user_id: str - The unique identifier for the user. - alias: Optional[str] - A human-friendly alias for the user. - blocked: bool - Flag to allow or disallow requests for this end-user. Default is False. - max_budget: Optional[float] - The maximum budget allocated to the user. Either &#39;max_budget&#39; or &#39;budget_id&#39; should be provided, not both. - budget_id: Optional[str] - The identifier for an existing budget allocated to the user. Either &#39;max_budget&#39; or &#39;budget_id&#39; should be provided, not both. - allowed_model_region: Optional[Union[Literal[\&quot;eu\&quot;], Literal[\&quot;us\&quot;]]] - Require all user requests to use models in this specific region. - default_model: Optional[str] - If no equivalent model in the allowed region, default all requests to this model. - metadata: Optional[dict] &#x3D; Metadata for customer, store information for customer. Example metadata &#x3D; {\&quot;data_training_opt_out\&quot;: True} - budget_duration: Optional[str] - Budget is reset at the end of specified duration. If not set, budget is never reset. You can set duration as seconds (\&quot;30s\&quot;), minutes (\&quot;30m\&quot;), hours (\&quot;30h\&quot;), days (\&quot;30d\&quot;). - tpm_limit: Optional[int] - [Not Implemented Yet] Specify tpm limit for a given customer (Tokens per minute) - rpm_limit: Optional[int] - [Not Implemented Yet] Specify rpm limit for a given customer (Requests per minute) - model_max_budget: Optional[dict] - [Not Implemented Yet] Specify max budget for a given model. Example: {\&quot;openai/gpt-4o-mini\&quot;: {\&quot;max_budget\&quot;: 100.0, \&quot;budget_duration\&quot;: \&quot;1d\&quot;}} - max_parallel_requests: Optional[int] - [Not Implemented Yet] Specify max parallel requests for a given customer. - soft_budget: Optional[float] - [Not Implemented Yet] Get alerts when customer crosses given budget, doesn&#39;t block requests. - spend: Optional[float] - Specify initial spend for a given customer.   - Allow specifying allowed regions  - Allow specifying default model  Example curl: &#x60;&#x60;&#x60; curl --location &#39;http://0.0.0.0:4000/customer/new&#39;         --header &#39;Authorization: Bearer sk-1234&#39;         --header &#39;Content-Type: application/json&#39;         --data &#39;{         \&quot;user_id\&quot; : \&quot;ishaan-jaff-3\&quot;,         \&quot;allowed_region\&quot;: \&quot;eu\&quot;,         \&quot;budget_id\&quot;: \&quot;free_tier\&quot;,         \&quot;default_model\&quot;: \&quot;azure/gpt-3.5-turbo-eu\&quot; &lt;- all calls from this user, use this model?      }&#39;      # return end-user object &#x60;&#x60;&#x60;  NOTE: This used to be called &#x60;/end_user/new&#x60;, we will still be maintaining compatibility for /end_user/XXX for these endpoints

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **NewCustomerRequest** | [**NewCustomerRequest**](../Models/NewCustomerRequest.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="unblockUserCustomerUnblockPost"></a>
# **unblockUserCustomerUnblockPost**
> oas_any_type_not_mapped unblockUserCustomerUnblockPost(BlockUsers)

Unblock User

    [BETA] Unblock calls with this user id  Example &#x60;&#x60;&#x60; curl -X POST \&quot;http://0.0.0.0:8000/user/unblock\&quot; -H \&quot;Authorization: Bearer sk-1234\&quot; -d &#39;{ \&quot;user_ids\&quot;: [&lt;user_id&gt;, ...] }&#39; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **BlockUsers** | [**BlockUsers**](../Models/BlockUsers.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="updateEndUserCustomerUpdatePost"></a>
# **updateEndUserCustomerUpdatePost**
> oas_any_type_not_mapped updateEndUserCustomerUpdatePost(UpdateCustomerRequest)

Update End User

    Example curl   Parameters: - user_id: str - alias: Optional[str] &#x3D; None  # human-friendly alias - blocked: bool &#x3D; False  # allow/disallow requests for this end-user - max_budget: Optional[float] &#x3D; None - budget_id: Optional[str] &#x3D; None  # give either a budget_id or max_budget - allowed_model_region: Optional[AllowedModelRegion] &#x3D; (     None  # require all user requests to use models in this specific region ) - default_model: Optional[str] &#x3D; (     None  # if no equivalent model in allowed region - default all requests to this model )  Example curl: &#x60;&#x60;&#x60; curl --location &#39;http://0.0.0.0:4000/customer/update&#39;     --header &#39;Authorization: Bearer sk-1234&#39;     --header &#39;Content-Type: application/json&#39;     --data &#39;{     \&quot;user_id\&quot;: \&quot;test-litellm-user-4\&quot;,     \&quot;budget_id\&quot;: \&quot;paid_tier\&quot; }&#39;  See below for all params  &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **UpdateCustomerRequest** | [**UpdateCustomerRequest**](../Models/UpdateCustomerRequest.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

