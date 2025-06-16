# KeyManagementApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**blockKeyKeyBlockPost**](KeyManagementApi.md#blockKeyKeyBlockPost) | **POST** /key/block | Block Key |
| [**deleteKeyFnKeyDeletePost**](KeyManagementApi.md#deleteKeyFnKeyDeletePost) | **POST** /key/delete | Delete Key Fn |
| [**generateKeyFnKeyGeneratePost**](KeyManagementApi.md#generateKeyFnKeyGeneratePost) | **POST** /key/generate | Generate Key Fn |
| [**infoKeyFnKeyInfoGet**](KeyManagementApi.md#infoKeyFnKeyInfoGet) | **GET** /key/info | Info Key Fn |
| [**keyHealthKeyHealthPost**](KeyManagementApi.md#keyHealthKeyHealthPost) | **POST** /key/health | Key Health |
| [**listKeysKeyListGet**](KeyManagementApi.md#listKeysKeyListGet) | **GET** /key/list | List Keys |
| [**regenerateKeyFnKeyKeyRegeneratePost**](KeyManagementApi.md#regenerateKeyFnKeyKeyRegeneratePost) | **POST** /key/{key}/regenerate | Regenerate Key Fn |
| [**regenerateKeyFnKeyRegeneratePost**](KeyManagementApi.md#regenerateKeyFnKeyRegeneratePost) | **POST** /key/regenerate | Regenerate Key Fn |
| [**unblockKeyKeyUnblockPost**](KeyManagementApi.md#unblockKeyKeyUnblockPost) | **POST** /key/unblock | Unblock Key |
| [**updateKeyFnKeyUpdatePost**](KeyManagementApi.md#updateKeyFnKeyUpdatePost) | **POST** /key/update | Update Key Fn |


<a name="blockKeyKeyBlockPost"></a>
# **blockKeyKeyBlockPost**
> LiteLLM_VerificationToken blockKeyKeyBlockPost(BlockKeyRequest, litellm-changed-by)

Block Key

    Block an Virtual key from making any requests.  Parameters: - key: str - The key to block. Can be either the unhashed key (sk-...) or the hashed key value   Example: &#x60;&#x60;&#x60;bash curl --location &#39;http://0.0.0.0:4000/key/block&#39;     --header &#39;Authorization: Bearer sk-1234&#39;     --header &#39;Content-Type: application/json&#39;     --data &#39;{     \&quot;key\&quot;: \&quot;sk-Fn8Ej39NxjAXrvpUGKghGw\&quot; }&#39; &#x60;&#x60;&#x60;  Note: This is an admin-only endpoint. Only proxy admins can block keys.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **BlockKeyRequest** | [**BlockKeyRequest**](../Models/BlockKeyRequest.md)|  | |
| **litellm-changed-by** | **String**| The litellm-changed-by header enables tracking of actions performed by authorized users on behalf of other users, providing an audit trail for accountability | [optional] [default to null] |

### Return type

[**LiteLLM_VerificationToken**](../Models/LiteLLM_VerificationToken.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="deleteKeyFnKeyDeletePost"></a>
# **deleteKeyFnKeyDeletePost**
> oas_any_type_not_mapped deleteKeyFnKeyDeletePost(KeyRequest, litellm-changed-by)

Delete Key Fn

    Delete a key from the key management system.  Parameters:: - keys (List[str]): A list of keys or hashed keys to delete. Example {\&quot;keys\&quot;: [\&quot;sk-QWrxEynunsNpV1zT48HIrw\&quot;, \&quot;837e17519f44683334df5291321d97b8bf1098cd490e49e215f6fea935aa28be\&quot;]} - key_aliases (List[str]): A list of key aliases to delete. Can be passed instead of &#x60;keys&#x60;.Example {\&quot;key_aliases\&quot;: [\&quot;alias1\&quot;, \&quot;alias2\&quot;]}  Returns: - deleted_keys (List[str]): A list of deleted keys. Example {\&quot;deleted_keys\&quot;: [\&quot;sk-QWrxEynunsNpV1zT48HIrw\&quot;, \&quot;837e17519f44683334df5291321d97b8bf1098cd490e49e215f6fea935aa28be\&quot;]}  Example: &#x60;&#x60;&#x60;bash curl --location &#39;http://0.0.0.0:4000/key/delete&#39;     --header &#39;Authorization: Bearer sk-1234&#39;     --header &#39;Content-Type: application/json&#39;     --data &#39;{     \&quot;keys\&quot;: [\&quot;sk-QWrxEynunsNpV1zT48HIrw\&quot;] }&#39; &#x60;&#x60;&#x60;  Raises:     HTTPException: If an error occurs during key deletion.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **KeyRequest** | [**KeyRequest**](../Models/KeyRequest.md)|  | |
| **litellm-changed-by** | **String**| The litellm-changed-by header enables tracking of actions performed by authorized users on behalf of other users, providing an audit trail for accountability | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="generateKeyFnKeyGeneratePost"></a>
# **generateKeyFnKeyGeneratePost**
> GenerateKeyResponse generateKeyFnKeyGeneratePost(GenerateKeyRequest, litellm-changed-by)

Generate Key Fn

    Generate an API key based on the provided data.  Docs: https://docs.litellm.ai/docs/proxy/virtual_keys  Parameters: - duration: Optional[str] - Specify the length of time the token is valid for. You can set duration as seconds (\&quot;30s\&quot;), minutes (\&quot;30m\&quot;), hours (\&quot;30h\&quot;), days (\&quot;30d\&quot;). - key_alias: Optional[str] - User defined key alias - key: Optional[str] - User defined key value. If not set, a 16-digit unique sk-key is created for you. - team_id: Optional[str] - The team id of the key - user_id: Optional[str] - The user id of the key - budget_id: Optional[str] - The budget id associated with the key. Created by calling &#x60;/budget/new&#x60;. - models: Optional[list] - Model_name&#39;s a user is allowed to call. (if empty, key is allowed to call all models) - aliases: Optional[dict] - Any alias mappings, on top of anything in the config.yaml model list. - https://docs.litellm.ai/docs/proxy/virtual_keys#managing-auth---upgradedowngrade-models - config: Optional[dict] - any key-specific configs, overrides config in config.yaml - spend: Optional[int] - Amount spent by key. Default is 0. Will be updated by proxy whenever key is used. https://docs.litellm.ai/docs/proxy/virtual_keys#managing-auth---tracking-spend - send_invite_email: Optional[bool] - Whether to send an invite email to the user_id, with the generate key - max_budget: Optional[float] - Specify max budget for a given key. - budget_duration: Optional[str] - Budget is reset at the end of specified duration. If not set, budget is never reset. You can set duration as seconds (\&quot;30s\&quot;), minutes (\&quot;30m\&quot;), hours (\&quot;30h\&quot;), days (\&quot;30d\&quot;). - max_parallel_requests: Optional[int] - Rate limit a user based on the number of parallel requests. Raises 429 error, if user&#39;s parallel requests &gt; x. - metadata: Optional[dict] - Metadata for key, store information for key. Example metadata &#x3D; {\&quot;team\&quot;: \&quot;core-infra\&quot;, \&quot;app\&quot;: \&quot;app2\&quot;, \&quot;email\&quot;: \&quot;ishaan@berri.ai\&quot; } - guardrails: Optional[List[str]] - List of active guardrails for the key - permissions: Optional[dict] - key-specific permissions. Currently just used for turning off pii masking (if connected). Example - {\&quot;pii\&quot;: false} - model_max_budget: Optional[Dict[str, BudgetConfig]] - Model-specific budgets {\&quot;gpt-4\&quot;: {\&quot;budget_limit\&quot;: 0.0005, \&quot;time_period\&quot;: \&quot;30d\&quot;}}}. IF null or {} then no model specific budget. - model_rpm_limit: Optional[dict] - key-specific model rpm limit. Example - {\&quot;text-davinci-002\&quot;: 1000, \&quot;gpt-3.5-turbo\&quot;: 1000}. IF null or {} then no model specific rpm limit. - model_tpm_limit: Optional[dict] - key-specific model tpm limit. Example - {\&quot;text-davinci-002\&quot;: 1000, \&quot;gpt-3.5-turbo\&quot;: 1000}. IF null or {} then no model specific tpm limit. - allowed_cache_controls: Optional[list] - List of allowed cache control values. Example - [\&quot;no-cache\&quot;, \&quot;no-store\&quot;]. See all values - https://docs.litellm.ai/docs/proxy/caching#turn-on--off-caching-per-request - blocked: Optional[bool] - Whether the key is blocked. - rpm_limit: Optional[int] - Specify rpm limit for a given key (Requests per minute) - tpm_limit: Optional[int] - Specify tpm limit for a given key (Tokens per minute) - soft_budget: Optional[float] - Specify soft budget for a given key. Will trigger a slack alert when this soft budget is reached. - tags: Optional[List[str]] - Tags for [tracking spend](https://litellm.vercel.app/docs/proxy/enterprise#tracking-spend-for-custom-tags) and/or doing [tag-based routing](https://litellm.vercel.app/docs/proxy/tag_routing). - enforced_params: Optional[List[str]] - List of enforced params for the key (Enterprise only). [Docs](https://docs.litellm.ai/docs/proxy/enterprise#enforce-required-params-for-llm-requests) - allowed_routes: Optional[list] - List of allowed routes for the key. Store the actual route or store a wildcard pattern for a set of routes. Example - [\&quot;/chat/completions\&quot;, \&quot;/embeddings\&quot;, \&quot;/keys/*\&quot;] - object_permission: Optional[LiteLLM_ObjectPermissionBase] - key-specific object permission. Example - {\&quot;vector_stores\&quot;: [\&quot;vector_store_1\&quot;, \&quot;vector_store_2\&quot;]}. IF null or {} then no object permission. Examples:  1. Allow users to turn on/off pii masking  &#x60;&#x60;&#x60;bash curl --location &#39;http://0.0.0.0:4000/key/generate&#39;         --header &#39;Authorization: Bearer sk-1234&#39;         --header &#39;Content-Type: application/json&#39;         --data &#39;{         \&quot;permissions\&quot;: {\&quot;allow_pii_controls\&quot;: true} }&#39; &#x60;&#x60;&#x60;  Returns: - key: (str) The generated api key - expires: (datetime) Datetime object for when key expires. - user_id: (str) Unique user id - used for tracking spend across multiple keys for same user id.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **GenerateKeyRequest** | [**GenerateKeyRequest**](../Models/GenerateKeyRequest.md)|  | |
| **litellm-changed-by** | **String**| The litellm-changed-by header enables tracking of actions performed by authorized users on behalf of other users, providing an audit trail for accountability | [optional] [default to null] |

### Return type

[**GenerateKeyResponse**](../Models/GenerateKeyResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="infoKeyFnKeyInfoGet"></a>
# **infoKeyFnKeyInfoGet**
> oas_any_type_not_mapped infoKeyFnKeyInfoGet(key)

Info Key Fn

    Retrieve information about a key. Parameters:     key: Optional[str] &#x3D; Query parameter representing the key in the request     user_api_key_dict: UserAPIKeyAuth &#x3D; Dependency representing the user&#39;s API key Returns:     Dict containing the key and its associated information  Example Curl: &#x60;&#x60;&#x60; curl -X GET \&quot;http://0.0.0.0:4000/key/info?key&#x3D;sk-02Wr4IAlN3NvPXvL5JVvDA\&quot; -H \&quot;Authorization: Bearer sk-1234\&quot; &#x60;&#x60;&#x60;  Example Curl - if no key is passed, it will use the Key Passed in Authorization Header &#x60;&#x60;&#x60; curl -X GET \&quot;http://0.0.0.0:4000/key/info\&quot; -H \&quot;Authorization: Bearer sk-02Wr4IAlN3NvPXvL5JVvDA\&quot; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **key** | **String**| Key in the request parameters | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="keyHealthKeyHealthPost"></a>
# **keyHealthKeyHealthPost**
> KeyHealthResponse keyHealthKeyHealthPost()

Key Health

    Check the health of the key  Checks: - If key based logging is configured correctly - sends a test log  Usage   Pass the key in the request header  &#x60;&#x60;&#x60;bash curl -X POST \&quot;http://localhost:4000/key/health\&quot;      -H \&quot;Authorization: Bearer sk-1234\&quot;      -H \&quot;Content-Type: application/json\&quot; &#x60;&#x60;&#x60;  Response when logging callbacks are setup correctly:  &#x60;&#x60;&#x60;json {   \&quot;key\&quot;: \&quot;healthy\&quot;,   \&quot;logging_callbacks\&quot;: {     \&quot;callbacks\&quot;: [       \&quot;gcs_bucket\&quot;     ],     \&quot;status\&quot;: \&quot;healthy\&quot;,     \&quot;details\&quot;: \&quot;No logger exceptions triggered, system is healthy. Manually check if logs were sent to [&#39;gcs_bucket&#39;]\&quot;   } } &#x60;&#x60;&#x60;   Response when logging callbacks are not setup correctly: &#x60;&#x60;&#x60;json {   \&quot;key\&quot;: \&quot;unhealthy\&quot;,   \&quot;logging_callbacks\&quot;: {     \&quot;callbacks\&quot;: [       \&quot;gcs_bucket\&quot;     ],     \&quot;status\&quot;: \&quot;unhealthy\&quot;,     \&quot;details\&quot;: \&quot;Logger exceptions triggered, system is unhealthy: Failed to load vertex credentials. Check to see if credentials containing partial/invalid information.\&quot;   } } &#x60;&#x60;&#x60;

### Parameters
This endpoint does not need any parameter.

### Return type

[**KeyHealthResponse**](../Models/KeyHealthResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="listKeysKeyListGet"></a>
# **listKeysKeyListGet**
> KeyListResponseObject listKeysKeyListGet(page, size, user\_id, team\_id, organization\_id, key\_hash, key\_alias, return\_full\_object, include\_team\_keys, sort\_by, sort\_order)

List Keys

    List all keys for a given user / team / organization.  Returns:     {         \&quot;keys\&quot;: List[str] or List[UserAPIKeyAuth],         \&quot;total_count\&quot;: int,         \&quot;current_page\&quot;: int,         \&quot;total_pages\&quot;: int,     }

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **page** | **Integer**| Page number | [optional] [default to 1] |
| **size** | **Integer**| Page size | [optional] [default to 10] |
| **user\_id** | **String**| Filter keys by user ID | [optional] [default to null] |
| **team\_id** | **String**| Filter keys by team ID | [optional] [default to null] |
| **organization\_id** | **String**| Filter keys by organization ID | [optional] [default to null] |
| **key\_hash** | **String**| Filter keys by key hash | [optional] [default to null] |
| **key\_alias** | **String**| Filter keys by key alias | [optional] [default to null] |
| **return\_full\_object** | **Boolean**| Return full key object | [optional] [default to false] |
| **include\_team\_keys** | **Boolean**| Include all keys for teams that user is an admin of. | [optional] [default to false] |
| **sort\_by** | **String**| Column to sort by (e.g. &#39;user_id&#39;, &#39;created_at&#39;, &#39;spend&#39;) | [optional] [default to null] |
| **sort\_order** | **String**| Sort order (&#39;asc&#39; or &#39;desc&#39;) | [optional] [default to desc] |

### Return type

[**KeyListResponseObject**](../Models/KeyListResponseObject.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="regenerateKeyFnKeyKeyRegeneratePost"></a>
# **regenerateKeyFnKeyKeyRegeneratePost**
> GenerateKeyResponse regenerateKeyFnKeyKeyRegeneratePost(key, litellm-changed-by, RegenerateKeyRequest)

Regenerate Key Fn

    Regenerate an existing API key while optionally updating its parameters.  Parameters: - key: str (path parameter) - The key to regenerate - data: Optional[RegenerateKeyRequest] - Request body containing optional parameters to update     - key_alias: Optional[str] - User-friendly key alias     - user_id: Optional[str] - User ID associated with key     - team_id: Optional[str] - Team ID associated with key     - models: Optional[list] - Model_name&#39;s a user is allowed to call     - tags: Optional[List[str]] - Tags for organizing keys (Enterprise only)     - spend: Optional[float] - Amount spent by key     - max_budget: Optional[float] - Max budget for key     - model_max_budget: Optional[Dict[str, BudgetConfig]] - Model-specific budgets {\&quot;gpt-4\&quot;: {\&quot;budget_limit\&quot;: 0.0005, \&quot;time_period\&quot;: \&quot;30d\&quot;}}     - budget_duration: Optional[str] - Budget reset period (\&quot;30d\&quot;, \&quot;1h\&quot;, etc.)     - soft_budget: Optional[float] - Soft budget limit (warning vs. hard stop). Will trigger a slack alert when this soft budget is reached.     - max_parallel_requests: Optional[int] - Rate limit for parallel requests     - metadata: Optional[dict] - Metadata for key. Example {\&quot;team\&quot;: \&quot;core-infra\&quot;, \&quot;app\&quot;: \&quot;app2\&quot;}     - tpm_limit: Optional[int] - Tokens per minute limit     - rpm_limit: Optional[int] - Requests per minute limit     - model_rpm_limit: Optional[dict] - Model-specific RPM limits {\&quot;gpt-4\&quot;: 100, \&quot;claude-v1\&quot;: 200}     - model_tpm_limit: Optional[dict] - Model-specific TPM limits {\&quot;gpt-4\&quot;: 100000, \&quot;claude-v1\&quot;: 200000}     - allowed_cache_controls: Optional[list] - List of allowed cache control values     - duration: Optional[str] - Key validity duration (\&quot;30d\&quot;, \&quot;1h\&quot;, etc.)     - permissions: Optional[dict] - Key-specific permissions     - guardrails: Optional[List[str]] - List of active guardrails for the key     - blocked: Optional[bool] - Whether the key is blocked   Returns: - GenerateKeyResponse containing the new key and its updated parameters  Example: &#x60;&#x60;&#x60;bash curl --location --request POST &#39;http://localhost:4000/key/sk-1234/regenerate&#39;     --header &#39;Authorization: Bearer sk-1234&#39;     --header &#39;Content-Type: application/json&#39;     --data-raw &#39;{     \&quot;max_budget\&quot;: 100,     \&quot;metadata\&quot;: {\&quot;team\&quot;: \&quot;core-infra\&quot;},     \&quot;models\&quot;: [\&quot;gpt-4\&quot;, \&quot;gpt-3.5-turbo\&quot;] }&#39; &#x60;&#x60;&#x60;  Note: This is an Enterprise feature. It requires a premium license to use.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **key** | **String**|  | [default to null] |
| **litellm-changed-by** | **String**| The litellm-changed-by header enables tracking of actions performed by authorized users on behalf of other users, providing an audit trail for accountability | [optional] [default to null] |
| **RegenerateKeyRequest** | [**RegenerateKeyRequest**](../Models/RegenerateKeyRequest.md)|  | [optional] |

### Return type

[**GenerateKeyResponse**](../Models/GenerateKeyResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="regenerateKeyFnKeyRegeneratePost"></a>
# **regenerateKeyFnKeyRegeneratePost**
> GenerateKeyResponse regenerateKeyFnKeyRegeneratePost(key, litellm-changed-by, RegenerateKeyRequest)

Regenerate Key Fn

    Regenerate an existing API key while optionally updating its parameters.  Parameters: - key: str (path parameter) - The key to regenerate - data: Optional[RegenerateKeyRequest] - Request body containing optional parameters to update     - key_alias: Optional[str] - User-friendly key alias     - user_id: Optional[str] - User ID associated with key     - team_id: Optional[str] - Team ID associated with key     - models: Optional[list] - Model_name&#39;s a user is allowed to call     - tags: Optional[List[str]] - Tags for organizing keys (Enterprise only)     - spend: Optional[float] - Amount spent by key     - max_budget: Optional[float] - Max budget for key     - model_max_budget: Optional[Dict[str, BudgetConfig]] - Model-specific budgets {\&quot;gpt-4\&quot;: {\&quot;budget_limit\&quot;: 0.0005, \&quot;time_period\&quot;: \&quot;30d\&quot;}}     - budget_duration: Optional[str] - Budget reset period (\&quot;30d\&quot;, \&quot;1h\&quot;, etc.)     - soft_budget: Optional[float] - Soft budget limit (warning vs. hard stop). Will trigger a slack alert when this soft budget is reached.     - max_parallel_requests: Optional[int] - Rate limit for parallel requests     - metadata: Optional[dict] - Metadata for key. Example {\&quot;team\&quot;: \&quot;core-infra\&quot;, \&quot;app\&quot;: \&quot;app2\&quot;}     - tpm_limit: Optional[int] - Tokens per minute limit     - rpm_limit: Optional[int] - Requests per minute limit     - model_rpm_limit: Optional[dict] - Model-specific RPM limits {\&quot;gpt-4\&quot;: 100, \&quot;claude-v1\&quot;: 200}     - model_tpm_limit: Optional[dict] - Model-specific TPM limits {\&quot;gpt-4\&quot;: 100000, \&quot;claude-v1\&quot;: 200000}     - allowed_cache_controls: Optional[list] - List of allowed cache control values     - duration: Optional[str] - Key validity duration (\&quot;30d\&quot;, \&quot;1h\&quot;, etc.)     - permissions: Optional[dict] - Key-specific permissions     - guardrails: Optional[List[str]] - List of active guardrails for the key     - blocked: Optional[bool] - Whether the key is blocked   Returns: - GenerateKeyResponse containing the new key and its updated parameters  Example: &#x60;&#x60;&#x60;bash curl --location --request POST &#39;http://localhost:4000/key/sk-1234/regenerate&#39;     --header &#39;Authorization: Bearer sk-1234&#39;     --header &#39;Content-Type: application/json&#39;     --data-raw &#39;{     \&quot;max_budget\&quot;: 100,     \&quot;metadata\&quot;: {\&quot;team\&quot;: \&quot;core-infra\&quot;},     \&quot;models\&quot;: [\&quot;gpt-4\&quot;, \&quot;gpt-3.5-turbo\&quot;] }&#39; &#x60;&#x60;&#x60;  Note: This is an Enterprise feature. It requires a premium license to use.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **key** | **String**|  | [optional] [default to null] |
| **litellm-changed-by** | **String**| The litellm-changed-by header enables tracking of actions performed by authorized users on behalf of other users, providing an audit trail for accountability | [optional] [default to null] |
| **RegenerateKeyRequest** | [**RegenerateKeyRequest**](../Models/RegenerateKeyRequest.md)|  | [optional] |

### Return type

[**GenerateKeyResponse**](../Models/GenerateKeyResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="unblockKeyKeyUnblockPost"></a>
# **unblockKeyKeyUnblockPost**
> oas_any_type_not_mapped unblockKeyKeyUnblockPost(BlockKeyRequest, litellm-changed-by)

Unblock Key

    Unblock a Virtual key to allow it to make requests again.  Parameters: - key: str - The key to unblock. Can be either the unhashed key (sk-...) or the hashed key value  Example: &#x60;&#x60;&#x60;bash curl --location &#39;http://0.0.0.0:4000/key/unblock&#39;     --header &#39;Authorization: Bearer sk-1234&#39;     --header &#39;Content-Type: application/json&#39;     --data &#39;{     \&quot;key\&quot;: \&quot;sk-Fn8Ej39NxjAXrvpUGKghGw\&quot; }&#39; &#x60;&#x60;&#x60;  Note: This is an admin-only endpoint. Only proxy admins can unblock keys.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **BlockKeyRequest** | [**BlockKeyRequest**](../Models/BlockKeyRequest.md)|  | |
| **litellm-changed-by** | **String**| The litellm-changed-by header enables tracking of actions performed by authorized users on behalf of other users, providing an audit trail for accountability | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="updateKeyFnKeyUpdatePost"></a>
# **updateKeyFnKeyUpdatePost**
> oas_any_type_not_mapped updateKeyFnKeyUpdatePost(UpdateKeyRequest, litellm-changed-by)

Update Key Fn

    Update an existing API key&#39;s parameters.  Parameters: - key: str - The key to update - key_alias: Optional[str] - User-friendly key alias - user_id: Optional[str] - User ID associated with key - team_id: Optional[str] - Team ID associated with key - budget_id: Optional[str] - The budget id associated with the key. Created by calling &#x60;/budget/new&#x60;. - models: Optional[list] - Model_name&#39;s a user is allowed to call - tags: Optional[List[str]] - Tags for organizing keys (Enterprise only) - enforced_params: Optional[List[str]] - List of enforced params for the key (Enterprise only). [Docs](https://docs.litellm.ai/docs/proxy/enterprise#enforce-required-params-for-llm-requests) - spend: Optional[float] - Amount spent by key - max_budget: Optional[float] - Max budget for key - model_max_budget: Optional[Dict[str, BudgetConfig]] - Model-specific budgets {\&quot;gpt-4\&quot;: {\&quot;budget_limit\&quot;: 0.0005, \&quot;time_period\&quot;: \&quot;30d\&quot;}} - budget_duration: Optional[str] - Budget reset period (\&quot;30d\&quot;, \&quot;1h\&quot;, etc.) - soft_budget: Optional[float] - [TODO] Soft budget limit (warning vs. hard stop). Will trigger a slack alert when this soft budget is reached. - max_parallel_requests: Optional[int] - Rate limit for parallel requests - metadata: Optional[dict] - Metadata for key. Example {\&quot;team\&quot;: \&quot;core-infra\&quot;, \&quot;app\&quot;: \&quot;app2\&quot;} - tpm_limit: Optional[int] - Tokens per minute limit - rpm_limit: Optional[int] - Requests per minute limit - model_rpm_limit: Optional[dict] - Model-specific RPM limits {\&quot;gpt-4\&quot;: 100, \&quot;claude-v1\&quot;: 200} - model_tpm_limit: Optional[dict] - Model-specific TPM limits {\&quot;gpt-4\&quot;: 100000, \&quot;claude-v1\&quot;: 200000} - allowed_cache_controls: Optional[list] - List of allowed cache control values - duration: Optional[str] - Key validity duration (\&quot;30d\&quot;, \&quot;1h\&quot;, etc.) - permissions: Optional[dict] - Key-specific permissions - send_invite_email: Optional[bool] - Send invite email to user_id - guardrails: Optional[List[str]] - List of active guardrails for the key - blocked: Optional[bool] - Whether the key is blocked - aliases: Optional[dict] - Model aliases for the key - [Docs](https://litellm.vercel.app/docs/proxy/virtual_keys#model-aliases) - config: Optional[dict] - [DEPRECATED PARAM] Key-specific config. - temp_budget_increase: Optional[float] - Temporary budget increase for the key (Enterprise only). - temp_budget_expiry: Optional[str] - Expiry time for the temporary budget increase (Enterprise only). - allowed_routes: Optional[list] - List of allowed routes for the key. Store the actual route or store a wildcard pattern for a set of routes. Example - [\&quot;/chat/completions\&quot;, \&quot;/embeddings\&quot;, \&quot;/keys/*\&quot;] - object_permission: Optional[LiteLLM_ObjectPermissionBase] - key-specific object permission. Example - {\&quot;vector_stores\&quot;: [\&quot;vector_store_1\&quot;, \&quot;vector_store_2\&quot;]}. IF null or {} then no object permission. Example: &#x60;&#x60;&#x60;bash curl --location &#39;http://0.0.0.0:4000/key/update&#39;     --header &#39;Authorization: Bearer sk-1234&#39;     --header &#39;Content-Type: application/json&#39;     --data &#39;{     \&quot;key\&quot;: \&quot;sk-1234\&quot;,     \&quot;key_alias\&quot;: \&quot;my-key\&quot;,     \&quot;user_id\&quot;: \&quot;user-1234\&quot;,     \&quot;team_id\&quot;: \&quot;team-1234\&quot;,     \&quot;max_budget\&quot;: 100,     \&quot;metadata\&quot;: {\&quot;any_key\&quot;: \&quot;any-val\&quot;}, }&#39; &#x60;&#x60;&#x60;

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **UpdateKeyRequest** | [**UpdateKeyRequest**](../Models/UpdateKeyRequest.md)|  | |
| **litellm-changed-by** | **String**| The litellm-changed-by header enables tracking of actions performed by authorized users on behalf of other users, providing an audit trail for accountability | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

