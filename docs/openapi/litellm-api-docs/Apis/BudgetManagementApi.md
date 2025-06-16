# BudgetManagementApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**budgetSettingsBudgetSettingsGet**](BudgetManagementApi.md#budgetSettingsBudgetSettingsGet) | **GET** /budget/settings | Budget Settings |
| [**deleteBudgetBudgetDeletePost**](BudgetManagementApi.md#deleteBudgetBudgetDeletePost) | **POST** /budget/delete | Delete Budget |
| [**infoBudgetBudgetInfoPost**](BudgetManagementApi.md#infoBudgetBudgetInfoPost) | **POST** /budget/info | Info Budget |
| [**listBudgetBudgetListGet**](BudgetManagementApi.md#listBudgetBudgetListGet) | **GET** /budget/list | List Budget |
| [**newBudgetBudgetNewPost**](BudgetManagementApi.md#newBudgetBudgetNewPost) | **POST** /budget/new | New Budget |
| [**updateBudgetBudgetUpdatePost**](BudgetManagementApi.md#updateBudgetBudgetUpdatePost) | **POST** /budget/update | Update Budget |


<a name="budgetSettingsBudgetSettingsGet"></a>
# **budgetSettingsBudgetSettingsGet**
> oas_any_type_not_mapped budgetSettingsBudgetSettingsGet(budget\_id)

Budget Settings

    Get list of configurable params + current value for a budget item + description of each field  Used on Admin UI.  Query Parameters: - budget_id: str - The budget id to get information for

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **budget\_id** | **String**|  | [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="deleteBudgetBudgetDeletePost"></a>
# **deleteBudgetBudgetDeletePost**
> oas_any_type_not_mapped deleteBudgetBudgetDeletePost(BudgetDeleteRequest)

Delete Budget

    Delete budget  Parameters: - id: str - The budget id to delete

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **BudgetDeleteRequest** | [**BudgetDeleteRequest**](../Models/BudgetDeleteRequest.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="infoBudgetBudgetInfoPost"></a>
# **infoBudgetBudgetInfoPost**
> oas_any_type_not_mapped infoBudgetBudgetInfoPost(BudgetRequest)

Info Budget

    Get the budget id specific information  Parameters: - budgets: List[str] - The list of budget ids to get information for

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **BudgetRequest** | [**BudgetRequest**](../Models/BudgetRequest.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="listBudgetBudgetListGet"></a>
# **listBudgetBudgetListGet**
> oas_any_type_not_mapped listBudgetBudgetListGet()

List Budget

    List all the created budgets in proxy db. Used on Admin UI.

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="newBudgetBudgetNewPost"></a>
# **newBudgetBudgetNewPost**
> oas_any_type_not_mapped newBudgetBudgetNewPost(BudgetNewRequest)

New Budget

    Create a new budget object. Can apply this to teams, orgs, end-users, keys.  Parameters: - budget_duration: Optional[str] - Budget reset period (\&quot;30d\&quot;, \&quot;1h\&quot;, etc.) - budget_id: Optional[str] - The id of the budget. If not provided, a new id will be generated. - max_budget: Optional[float] - The max budget for the budget. - soft_budget: Optional[float] - The soft budget for the budget. - max_parallel_requests: Optional[int] - The max number of parallel requests for the budget. - tpm_limit: Optional[int] - The tokens per minute limit for the budget. - rpm_limit: Optional[int] - The requests per minute limit for the budget. - model_max_budget: Optional[dict] - Specify max budget for a given model. Example: {\&quot;openai/gpt-4o-mini\&quot;: {\&quot;max_budget\&quot;: 100.0, \&quot;budget_duration\&quot;: \&quot;1d\&quot;, \&quot;tpm_limit\&quot;: 100000, \&quot;rpm_limit\&quot;: 100000}}

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **BudgetNewRequest** | [**BudgetNewRequest**](../Models/BudgetNewRequest.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="updateBudgetBudgetUpdatePost"></a>
# **updateBudgetBudgetUpdatePost**
> oas_any_type_not_mapped updateBudgetBudgetUpdatePost(BudgetNewRequest)

Update Budget

    Update an existing budget object.  Parameters: - budget_duration: Optional[str] - Budget reset period (\&quot;30d\&quot;, \&quot;1h\&quot;, etc.) - budget_id: Optional[str] - The id of the budget. If not provided, a new id will be generated. - max_budget: Optional[float] - The max budget for the budget. - soft_budget: Optional[float] - The soft budget for the budget. - max_parallel_requests: Optional[int] - The max number of parallel requests for the budget. - tpm_limit: Optional[int] - The tokens per minute limit for the budget. - rpm_limit: Optional[int] - The requests per minute limit for the budget. - model_max_budget: Optional[dict] - Specify max budget for a given model. Example: {\&quot;openai/gpt-4o-mini\&quot;: {\&quot;max_budget\&quot;: 100.0, \&quot;budget_duration\&quot;: \&quot;1d\&quot;, \&quot;tpm_limit\&quot;: 100000, \&quot;rpm_limit\&quot;: 100000}}

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **BudgetNewRequest** | [**BudgetNewRequest**](../Models/BudgetNewRequest.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

