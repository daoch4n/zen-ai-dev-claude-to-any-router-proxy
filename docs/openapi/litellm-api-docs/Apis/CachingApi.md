# CachingApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**cacheDeleteCacheDeletePost**](CachingApi.md#cacheDeleteCacheDeletePost) | **POST** /cache/delete | Cache Delete |
| [**cacheDeleteCacheDeletePost_0**](CachingApi.md#cacheDeleteCacheDeletePost_0) | **POST** /cache/delete | Cache Delete |
| [**cacheFlushallCacheFlushallPost**](CachingApi.md#cacheFlushallCacheFlushallPost) | **POST** /cache/flushall | Cache Flushall |
| [**cacheFlushallCacheFlushallPost_0**](CachingApi.md#cacheFlushallCacheFlushallPost_0) | **POST** /cache/flushall | Cache Flushall |
| [**cachePingCachePingGet**](CachingApi.md#cachePingCachePingGet) | **GET** /cache/ping | Cache Ping |
| [**cacheRedisInfoCacheRedisInfoGet**](CachingApi.md#cacheRedisInfoCacheRedisInfoGet) | **GET** /cache/redis/info | Cache Redis Info |


<a name="cacheDeleteCacheDeletePost"></a>
# **cacheDeleteCacheDeletePost**
> oas_any_type_not_mapped cacheDeleteCacheDeletePost()

Cache Delete

    Endpoint for deleting a key from the cache. All responses from litellm proxy have &#x60;x-litellm-cache-key&#x60; in the headers  Parameters: - **keys**: *Optional[List[str]]* - A list of keys to delete from the cache. Example {\&quot;keys\&quot;: [\&quot;key1\&quot;, \&quot;key2\&quot;]}  &#x60;&#x60;&#x60;shell curl -X POST \&quot;http://0.0.0.0:4000/cache/delete\&quot;     -H \&quot;Authorization: Bearer sk-1234\&quot;     -d &#39;{\&quot;keys\&quot;: [\&quot;key1\&quot;, \&quot;key2\&quot;]}&#39; &#x60;&#x60;&#x60;

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="cacheDeleteCacheDeletePost_0"></a>
# **cacheDeleteCacheDeletePost_0**
> oas_any_type_not_mapped cacheDeleteCacheDeletePost_0()

Cache Delete

    Endpoint for deleting a key from the cache. All responses from litellm proxy have &#x60;x-litellm-cache-key&#x60; in the headers  Parameters: - **keys**: *Optional[List[str]]* - A list of keys to delete from the cache. Example {\&quot;keys\&quot;: [\&quot;key1\&quot;, \&quot;key2\&quot;]}  &#x60;&#x60;&#x60;shell curl -X POST \&quot;http://0.0.0.0:4000/cache/delete\&quot;     -H \&quot;Authorization: Bearer sk-1234\&quot;     -d &#39;{\&quot;keys\&quot;: [\&quot;key1\&quot;, \&quot;key2\&quot;]}&#39; &#x60;&#x60;&#x60;

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="cacheFlushallCacheFlushallPost"></a>
# **cacheFlushallCacheFlushallPost**
> oas_any_type_not_mapped cacheFlushallCacheFlushallPost()

Cache Flushall

    A function to flush all items from the cache. (All items will be deleted from the cache with this) Raises HTTPException if the cache is not initialized or if the cache type does not support flushing. Returns a dictionary with the status of the operation.  Usage: &#x60;&#x60;&#x60; curl -X POST http://0.0.0.0:4000/cache/flushall -H \&quot;Authorization: Bearer sk-1234\&quot; &#x60;&#x60;&#x60;

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="cacheFlushallCacheFlushallPost_0"></a>
# **cacheFlushallCacheFlushallPost_0**
> oas_any_type_not_mapped cacheFlushallCacheFlushallPost_0()

Cache Flushall

    A function to flush all items from the cache. (All items will be deleted from the cache with this) Raises HTTPException if the cache is not initialized or if the cache type does not support flushing. Returns a dictionary with the status of the operation.  Usage: &#x60;&#x60;&#x60; curl -X POST http://0.0.0.0:4000/cache/flushall -H \&quot;Authorization: Bearer sk-1234\&quot; &#x60;&#x60;&#x60;

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="cachePingCachePingGet"></a>
# **cachePingCachePingGet**
> CachePingResponse cachePingCachePingGet()

Cache Ping

    Endpoint for checking if cache can be pinged

### Parameters
This endpoint does not need any parameter.

### Return type

[**CachePingResponse**](../Models/CachePingResponse.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="cacheRedisInfoCacheRedisInfoGet"></a>
# **cacheRedisInfoCacheRedisInfoGet**
> oas_any_type_not_mapped cacheRedisInfoCacheRedisInfoGet()

Cache Redis Info

    Endpoint for getting /redis/info

### Parameters
This endpoint does not need any parameter.

### Return type

[**oas_any_type_not_mapped**](../Models/AnyType.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

