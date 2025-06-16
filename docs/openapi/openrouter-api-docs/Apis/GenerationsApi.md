# GenerationsApi

All URIs are relative to *https://openrouter.ai/api/v1*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getGeneration**](GenerationsApi.md#getGeneration) | **GET** /generation | Get generation details |


<a name="getGeneration"></a>
# **getGeneration**
> Generation getGeneration(id)

Get generation details

    Retrieve detailed information about a specific generation

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **id** | **String**| Generation ID returned from chat completion | [default to null] |

### Return type

[**Generation**](../Models/Generation.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

