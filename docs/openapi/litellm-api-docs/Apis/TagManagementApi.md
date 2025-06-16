# TagManagementApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**deleteTagTagDeletePost**](TagManagementApi.md#deleteTagTagDeletePost) | **POST** /tag/delete | Delete Tag |
| [**getTagDailyActivityTagDailyActivityGet**](TagManagementApi.md#getTagDailyActivityTagDailyActivityGet) | **GET** /tag/daily/activity | Get Tag Daily Activity |
| [**infoTagTagInfoPost**](TagManagementApi.md#infoTagTagInfoPost) | **POST** /tag/info | Info Tag |
| [**listTagsTagListGet**](TagManagementApi.md#listTagsTagListGet) | **GET** /tag/list | List Tags |
| [**newTagTagNewPost**](TagManagementApi.md#newTagTagNewPost) | **POST** /tag/new | New Tag |
| [**updateTagTagUpdatePost**](TagManagementApi.md#updateTagTagUpdatePost) | **POST** /tag/update | Update Tag |


<a name="deleteTagTagDeletePost"></a>
# **deleteTagTagDeletePost**
> oas_any_type_not_mapped deleteTagTagDeletePost(TagDeleteRequest)

Delete Tag

    Delete a tag.  Parameters: - name: str - The name of the tag to delete

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **TagDeleteRequest** | [**TagDeleteRequest**](../Models/TagDeleteRequest.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="getTagDailyActivityTagDailyActivityGet"></a>
# **getTagDailyActivityTagDailyActivityGet**
> SpendAnalyticsPaginatedResponse getTagDailyActivityTagDailyActivityGet(tags, start\_date, end\_date, model, api\_key, page, page\_size)

Get Tag Daily Activity

    Get daily activity for specific tags or all tags.  Args:     tags (Optional[str]): Comma-separated list of tags to filter by. If not provided, returns data for all tags.     start_date (Optional[str]): Start date for the activity period (YYYY-MM-DD).     end_date (Optional[str]): End date for the activity period (YYYY-MM-DD).     model (Optional[str]): Filter by model name.     api_key (Optional[str]): Filter by API key.     page (int): Page number for pagination.     page_size (int): Number of items per page.  Returns:     SpendAnalyticsPaginatedResponse: Paginated response containing daily activity data.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **tags** | **String**|  | [optional] [default to null] |
| **start\_date** | **String**|  | [optional] [default to null] |
| **end\_date** | **String**|  | [optional] [default to null] |
| **model** | **String**|  | [optional] [default to null] |
| **api\_key** | **String**|  | [optional] [default to null] |
| **page** | **Integer**|  | [optional] [default to 1] |
| **page\_size** | **Integer**|  | [optional] [default to 10] |

### Return type

[**SpendAnalyticsPaginatedResponse**](../Models/SpendAnalyticsPaginatedResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="infoTagTagInfoPost"></a>
# **infoTagTagInfoPost**
> oas_any_type_not_mapped infoTagTagInfoPost(TagInfoRequest)

Info Tag

    Get information about specific tags.  Parameters: - names: List[str] - List of tag names to get information for

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **TagInfoRequest** | [**TagInfoRequest**](../Models/TagInfoRequest.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="listTagsTagListGet"></a>
# **listTagsTagListGet**
> List listTagsTagListGet()

List Tags

    List all available tags.

### Parameters
This endpoint does not need any parameter.

### Return type

[**List**](../Models/TagConfig.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="newTagTagNewPost"></a>
# **newTagTagNewPost**
> oas_any_type_not_mapped newTagTagNewPost(TagNewRequest)

New Tag

    Create a new tag.  Parameters: - name: str - The name of the tag - description: Optional[str] - Description of what this tag represents - models: List[str] - List of LLM models allowed for this tag

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **TagNewRequest** | [**TagNewRequest**](../Models/TagNewRequest.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="updateTagTagUpdatePost"></a>
# **updateTagTagUpdatePost**
> oas_any_type_not_mapped updateTagTagUpdatePost(TagUpdateRequest)

Update Tag

    Update an existing tag.  Parameters: - name: str - The name of the tag to update - description: Optional[str] - Updated description - models: List[str] - Updated list of allowed LLM models

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **TagUpdateRequest** | [**TagUpdateRequest**](../Models/TagUpdateRequest.md)|  | |

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

