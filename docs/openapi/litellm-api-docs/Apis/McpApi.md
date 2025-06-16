# McpApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**addMcpServerV1McpServerPost**](McpApi.md#addMcpServerV1McpServerPost) | **POST** /v1/mcp/server | Add Mcp Server |
| [**callToolRestApiMcpToolsCallPost**](McpApi.md#callToolRestApiMcpToolsCallPost) | **POST** /mcp/tools/call | Call Tool Rest Api |
| [**editMcpServerV1McpServerPut**](McpApi.md#editMcpServerV1McpServerPut) | **PUT** /v1/mcp/server | Edit Mcp Server |
| [**fetchAllMcpServersV1McpServerGet**](McpApi.md#fetchAllMcpServersV1McpServerGet) | **GET** /v1/mcp/server | Fetch All Mcp Servers |
| [**fetchMcpServerV1McpServerServerIdGet**](McpApi.md#fetchMcpServerV1McpServerServerIdGet) | **GET** /v1/mcp/server/{server_id} | Fetch Mcp Server |
| [**getMcpServerEnabledMcpEnabledGet**](McpApi.md#getMcpServerEnabledMcpEnabledGet) | **GET** /mcp/enabled | Get Mcp Server Enabled |
| [**handleMessagesMcpSseMessagesPost**](McpApi.md#handleMessagesMcpSseMessagesPost) | **POST** /mcp/sse/messages | Handle Messages |
| [**handleSseMcpGet**](McpApi.md#handleSseMcpGet) | **GET** /mcp/ | Handle Sse |
| [**listToolRestApiMcpToolsListGet**](McpApi.md#listToolRestApiMcpToolsListGet) | **GET** /mcp/tools/list | List Tool Rest Api |
| [**removeMcpServerV1McpServerServerIdDelete**](McpApi.md#removeMcpServerV1McpServerServerIdDelete) | **DELETE** /v1/mcp/server/{server_id} | Remove Mcp Server |


<a name="addMcpServerV1McpServerPost"></a>
# **addMcpServerV1McpServerPost**
> LiteLLM_MCPServerTable addMcpServerV1McpServerPost(NewMCPServerRequest, litellm-changed-by)

Add Mcp Server

    Allows creation of mcp servers

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **NewMCPServerRequest** | [**NewMCPServerRequest**](../Models/NewMCPServerRequest.md)|  | |
| **litellm-changed-by** | **String**| The litellm-changed-by header enables tracking of actions performed by authorized users on behalf of other users, providing an audit trail for accountability | [optional] [default to null] |

### Return type

[**LiteLLM_MCPServerTable**](../Models/LiteLLM_MCPServerTable.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="callToolRestApiMcpToolsCallPost"></a>
# **callToolRestApiMcpToolsCallPost**
> oas_any_type_not_mapped callToolRestApiMcpToolsCallPost()

Call Tool Rest Api

    REST API to call a specific MCP tool with the provided arguments

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="editMcpServerV1McpServerPut"></a>
# **editMcpServerV1McpServerPut**
> LiteLLM_MCPServerTable editMcpServerV1McpServerPut(UpdateMCPServerRequest, litellm-changed-by)

Edit Mcp Server

    Allows deleting mcp serves in the db

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **UpdateMCPServerRequest** | [**UpdateMCPServerRequest**](../Models/UpdateMCPServerRequest.md)|  | |
| **litellm-changed-by** | **String**| The litellm-changed-by header enables tracking of actions performed by authorized users on behalf of other users, providing an audit trail for accountability | [optional] [default to null] |

### Return type

[**LiteLLM_MCPServerTable**](../Models/LiteLLM_MCPServerTable.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="fetchAllMcpServersV1McpServerGet"></a>
# **fetchAllMcpServersV1McpServerGet**
> List fetchAllMcpServersV1McpServerGet()

Fetch All Mcp Servers

    Returns the mcp server list

### Parameters
This endpoint does not need any parameter.

### Return type

[**List**](../Models/LiteLLM_MCPServerTable.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="fetchMcpServerV1McpServerServerIdGet"></a>
# **fetchMcpServerV1McpServerServerIdGet**
> LiteLLM_MCPServerTable fetchMcpServerV1McpServerServerIdGet(server\_id)

Fetch Mcp Server

    Returns the mcp server info

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **server\_id** | **String**|  | [default to null] |

### Return type

[**LiteLLM_MCPServerTable**](../Models/LiteLLM_MCPServerTable.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getMcpServerEnabledMcpEnabledGet"></a>
# **getMcpServerEnabledMcpEnabledGet**
> Map getMcpServerEnabledMcpEnabledGet()

Get Mcp Server Enabled

    Returns if the MCP server is enabled

### Parameters
This endpoint does not need any parameter.

### Return type

**Map**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="handleMessagesMcpSseMessagesPost"></a>
# **handleMessagesMcpSseMessagesPost**
> oas_any_type_not_mapped handleMessagesMcpSseMessagesPost()

Handle Messages

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="handleSseMcpGet"></a>
# **handleSseMcpGet**
> handleSseMcpGet()

Handle Sse

### Parameters
This endpoint does not need any parameter.

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined

<a name="listToolRestApiMcpToolsListGet"></a>
# **listToolRestApiMcpToolsListGet**
> List listToolRestApiMcpToolsListGet(server\_id)

List Tool Rest Api

    List all available tools with information about the server they belong to.  Example response: Tools: [     {         \&quot;name\&quot;: \&quot;create_zap\&quot;,         \&quot;description\&quot;: \&quot;Create a new zap\&quot;,         \&quot;inputSchema\&quot;: \&quot;tool_input_schema\&quot;,         \&quot;mcp_info\&quot;: {             \&quot;server_name\&quot;: \&quot;zapier\&quot;,             \&quot;logo_url\&quot;: \&quot;https://www.zapier.com/logo.png\&quot;,         }     },     {         \&quot;name\&quot;: \&quot;fetch_data\&quot;,         \&quot;description\&quot;: \&quot;Fetch data from a URL\&quot;,         \&quot;inputSchema\&quot;: \&quot;tool_input_schema\&quot;,         \&quot;mcp_info\&quot;: {             \&quot;server_name\&quot;: \&quot;fetch\&quot;,             \&quot;logo_url\&quot;: \&quot;https://www.fetch.com/logo.png\&quot;,         }     } ]

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **server\_id** | **String**| The server id to list tools for | [optional] [default to null] |

### Return type

[**List**](../Models/ListMCPToolsRestAPIResponseObject.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="removeMcpServerV1McpServerServerIdDelete"></a>
# **removeMcpServerV1McpServerServerIdDelete**
> oas_any_type_not_mapped removeMcpServerV1McpServerServerIdDelete(server\_id, litellm-changed-by)

Remove Mcp Server

    Allows deleting mcp serves in the db

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **server\_id** | **String**|  | [default to null] |
| **litellm-changed-by** | **String**| The litellm-changed-by header enables tracking of actions performed by authorized users on behalf of other users, providing an audit trail for accountability | [optional] [default to null] |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

