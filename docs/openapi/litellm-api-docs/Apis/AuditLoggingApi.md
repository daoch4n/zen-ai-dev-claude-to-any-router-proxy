# AuditLoggingApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getAuditLogByIdAuditIdGet**](AuditLoggingApi.md#getAuditLogByIdAuditIdGet) | **GET** /audit/{id} | Get Audit Log By Id |
| [**getAuditLogsAuditGet**](AuditLoggingApi.md#getAuditLogsAuditGet) | **GET** /audit | Get Audit Logs |


<a name="getAuditLogByIdAuditIdGet"></a>
# **getAuditLogByIdAuditIdGet**
> AuditLogResponse getAuditLogByIdAuditIdGet(id)

Get Audit Log By Id

    Get detailed information about a specific audit log entry by its ID.  Args:     id (str): The unique identifier of the audit log entry  Returns:     AuditLogResponse: Detailed information about the audit log entry  Raises:     HTTPException: If the audit log is not found or if there&#39;s a database connection error

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **id** | **String**|  | [default to null] |

### Return type

[**AuditLogResponse**](../Models/AuditLogResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getAuditLogsAuditGet"></a>
# **getAuditLogsAuditGet**
> PaginatedAuditLogResponse getAuditLogsAuditGet(page, page\_size, changed\_by, changed\_by\_api\_key, action, table\_name, object\_id, start\_date, end\_date, sort\_by, sort\_order)

Get Audit Logs

    Get all audit logs with filtering and pagination.  Returns a paginated response of audit logs matching the specified filters.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **page** | **Integer**|  | [optional] [default to 1] |
| **page\_size** | **Integer**|  | [optional] [default to 10] |
| **changed\_by** | **String**| Filter by user or system that performed the action | [optional] [default to null] |
| **changed\_by\_api\_key** | **String**| Filter by API key hash that performed the action | [optional] [default to null] |
| **action** | **String**| Filter by action type (create, update, delete) | [optional] [default to null] |
| **table\_name** | **String**| Filter by table name that was modified | [optional] [default to null] |
| **object\_id** | **String**| Filter by ID of the object that was modified | [optional] [default to null] |
| **start\_date** | **String**| Filter logs after this date | [optional] [default to null] |
| **end\_date** | **String**| Filter logs before this date | [optional] [default to null] |
| **sort\_by** | **String**| Column to sort by (e.g. &#39;updated_at&#39;, &#39;action&#39;, &#39;table_name&#39;) | [optional] [default to null] |
| **sort\_order** | **String**| Sort order (&#39;asc&#39; or &#39;desc&#39;) | [optional] [default to desc] |

### Return type

[**PaginatedAuditLogResponse**](../Models/PaginatedAuditLogResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

