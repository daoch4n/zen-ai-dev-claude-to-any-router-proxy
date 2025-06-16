# MessageBatchesApi

All URIs are relative to *https://api.anthropic.com*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**betaMessageBatchesCancel**](MessageBatchesApi.md#betaMessageBatchesCancel) | **POST** /v1/messages/batches/{message_batch_id}/cancel?beta&#x3D;true | Cancel a Message Batch |
| [**betaMessageBatchesCancel_0**](MessageBatchesApi.md#betaMessageBatchesCancel_0) | **POST** /v1/messages/batches/{message_batch_id}/cancel | Cancel a Message Batch |
| [**betaMessageBatchesList**](MessageBatchesApi.md#betaMessageBatchesList) | **GET** /v1/messages/batches?beta&#x3D;true | List Message Batches |
| [**betaMessageBatchesList_0**](MessageBatchesApi.md#betaMessageBatchesList_0) | **GET** /v1/messages/batches | List Message Batches |
| [**betaMessageBatchesPost**](MessageBatchesApi.md#betaMessageBatchesPost) | **POST** /v1/messages/batches?beta&#x3D;true | Create a Message Batch |
| [**betaMessageBatchesPost_0**](MessageBatchesApi.md#betaMessageBatchesPost_0) | **POST** /v1/messages/batches | Create a Message Batch |
| [**betaMessageBatchesResults**](MessageBatchesApi.md#betaMessageBatchesResults) | **GET** /v1/messages/batches/{message_batch_id}/results?beta&#x3D;true | Retrieve Message Batch results |
| [**betaMessageBatchesResults_0**](MessageBatchesApi.md#betaMessageBatchesResults_0) | **GET** /v1/messages/batches/{message_batch_id}/results | Retrieve Message Batch results |
| [**betaMessageBatchesRetrieve**](MessageBatchesApi.md#betaMessageBatchesRetrieve) | **GET** /v1/messages/batches/{message_batch_id}?beta&#x3D;true | Retrieve a Message Batch |
| [**betaMessageBatchesRetrieve_0**](MessageBatchesApi.md#betaMessageBatchesRetrieve_0) | **GET** /v1/messages/batches/{message_batch_id} | Retrieve a Message Batch |


<a name="betaMessageBatchesCancel"></a>
# **betaMessageBatchesCancel**
> BetaMessageBatch betaMessageBatchesCancel(message\_batch\_id, anthropic-beta, anthropic-version)

Cancel a Message Batch

    Batches may be canceled any time before processing ends. Once cancellation is initiated, the batch enters a &#x60;canceling&#x60; state, at which time the system may complete any in-progress, non-interruptible requests before finalizing cancellation.  The number of canceled requests is specified in &#x60;request_counts&#x60;. To determine which requests were canceled, check the individual results within the batch. Note that cancellation may not result in any canceled requests if they were non-interruptible.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **message\_batch\_id** | **String**| ID of the Message Batch. | [default to null] |
| **anthropic-beta** | **String**| Optional header to specify the beta version(s) you want to use.  To use multiple betas, use a comma separated list like &#x60;beta1,beta2&#x60; or specify the header multiple times for each beta. | [optional] [default to null] |
| **anthropic-version** | **String**| The version of the Anthropic API you want to use.  Read more about versioning and our version history [here](https://docs.anthropic.com/en/api/versioning). | [optional] [default to null] |

### Return type

[**BetaMessageBatch**](../Models/BetaMessageBatch.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="betaMessageBatchesCancel_0"></a>
# **betaMessageBatchesCancel_0**
> BetaMessageBatch betaMessageBatchesCancel_0(message\_batch\_id, anthropic-beta, anthropic-version)

Cancel a Message Batch

    Batches may be canceled any time before processing ends. Once cancellation is initiated, the batch enters a &#x60;canceling&#x60; state, at which time the system may complete any in-progress, non-interruptible requests before finalizing cancellation.  The number of canceled requests is specified in &#x60;request_counts&#x60;. To determine which requests were canceled, check the individual results within the batch. Note that cancellation may not result in any canceled requests if they were non-interruptible.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **message\_batch\_id** | **String**| ID of the Message Batch. | [default to null] |
| **anthropic-beta** | **String**| Optional header to specify the beta version(s) you want to use.  To use multiple betas, use a comma separated list like &#x60;beta1,beta2&#x60; or specify the header multiple times for each beta. | [optional] [default to null] |
| **anthropic-version** | **String**| The version of the Anthropic API you want to use.  Read more about versioning and our version history [here](https://docs.anthropic.com/en/api/versioning). | [optional] [default to null] |

### Return type

[**BetaMessageBatch**](../Models/BetaMessageBatch.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="betaMessageBatchesList"></a>
# **betaMessageBatchesList**
> BetaListResponse_MessageBatch_ betaMessageBatchesList(before\_id, after\_id, limit, anthropic-beta, anthropic-version, x-api-key)

List Message Batches

    List all Message Batches within a Workspace. Most recently created batches are returned first.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **before\_id** | **String**| ID of the object to use as a cursor for pagination. When provided, returns the page of results immediately before this object. | [optional] [default to null] |
| **after\_id** | **String**| ID of the object to use as a cursor for pagination. When provided, returns the page of results immediately after this object. | [optional] [default to null] |
| **limit** | **Integer**| Number of items to return per page.  Defaults to &#x60;20&#x60;. Ranges from &#x60;1&#x60; to &#x60;100&#x60;. | [optional] [default to 20] |
| **anthropic-beta** | **String**| Optional header to specify the beta version(s) you want to use.  To use multiple betas, use a comma separated list like &#x60;beta1,beta2&#x60; or specify the header multiple times for each beta. | [optional] [default to null] |
| **anthropic-version** | **String**| The version of the Anthropic API you want to use.  Read more about versioning and our version history [here](https://docs.anthropic.com/en/api/versioning). | [optional] [default to null] |
| **x-api-key** | **String**| Your unique API key for authentication.   This key is required in the header of all API requests, to authenticate your account and access Anthropic&#39;s services. Get your API key through the [Console](https://console.anthropic.com/settings/keys). Each key is scoped to a Workspace. | [optional] [default to null] |

### Return type

[**BetaListResponse_MessageBatch_**](../Models/BetaListResponse_MessageBatch_.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="betaMessageBatchesList_0"></a>
# **betaMessageBatchesList_0**
> BetaListResponse_MessageBatch_ betaMessageBatchesList_0(before\_id, after\_id, limit, anthropic-beta, anthropic-version, x-api-key)

List Message Batches

    List all Message Batches within a Workspace. Most recently created batches are returned first.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **before\_id** | **String**| ID of the object to use as a cursor for pagination. When provided, returns the page of results immediately before this object. | [optional] [default to null] |
| **after\_id** | **String**| ID of the object to use as a cursor for pagination. When provided, returns the page of results immediately after this object. | [optional] [default to null] |
| **limit** | **Integer**| Number of items to return per page.  Defaults to &#x60;20&#x60;. Ranges from &#x60;1&#x60; to &#x60;100&#x60;. | [optional] [default to 20] |
| **anthropic-beta** | **String**| Optional header to specify the beta version(s) you want to use.  To use multiple betas, use a comma separated list like &#x60;beta1,beta2&#x60; or specify the header multiple times for each beta. | [optional] [default to null] |
| **anthropic-version** | **String**| The version of the Anthropic API you want to use.  Read more about versioning and our version history [here](https://docs.anthropic.com/en/api/versioning). | [optional] [default to null] |
| **x-api-key** | **String**| Your unique API key for authentication.   This key is required in the header of all API requests, to authenticate your account and access Anthropic&#39;s services. Get your API key through the [Console](https://console.anthropic.com/settings/keys). Each key is scoped to a Workspace. | [optional] [default to null] |

### Return type

[**BetaListResponse_MessageBatch_**](../Models/BetaListResponse_MessageBatch_.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="betaMessageBatchesPost"></a>
# **betaMessageBatchesPost**
> BetaMessageBatch betaMessageBatchesPost(BetaCreateMessageBatchParams, anthropic-beta, anthropic-version)

Create a Message Batch

    Send a batch of Message creation requests.  The Message Batches API can be used to process multiple Messages API requests at once. Once a Message Batch is created, it begins processing immediately. Batches can take up to 24 hours to complete.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **BetaCreateMessageBatchParams** | [**BetaCreateMessageBatchParams**](../Models/BetaCreateMessageBatchParams.md)|  | |
| **anthropic-beta** | **String**| Optional header to specify the beta version(s) you want to use.  To use multiple betas, use a comma separated list like &#x60;beta1,beta2&#x60; or specify the header multiple times for each beta. | [optional] [default to null] |
| **anthropic-version** | **String**| The version of the Anthropic API you want to use.  Read more about versioning and our version history [here](https://docs.anthropic.com/en/api/versioning). | [optional] [default to null] |

### Return type

[**BetaMessageBatch**](../Models/BetaMessageBatch.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="betaMessageBatchesPost_0"></a>
# **betaMessageBatchesPost_0**
> BetaMessageBatch betaMessageBatchesPost_0(BetaCreateMessageBatchParams, anthropic-beta, anthropic-version)

Create a Message Batch

    Send a batch of Message creation requests.  The Message Batches API can be used to process multiple Messages API requests at once. Once a Message Batch is created, it begins processing immediately. Batches can take up to 24 hours to complete.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **BetaCreateMessageBatchParams** | [**BetaCreateMessageBatchParams**](../Models/BetaCreateMessageBatchParams.md)|  | |
| **anthropic-beta** | **String**| Optional header to specify the beta version(s) you want to use.  To use multiple betas, use a comma separated list like &#x60;beta1,beta2&#x60; or specify the header multiple times for each beta. | [optional] [default to null] |
| **anthropic-version** | **String**| The version of the Anthropic API you want to use.  Read more about versioning and our version history [here](https://docs.anthropic.com/en/api/versioning). | [optional] [default to null] |

### Return type

[**BetaMessageBatch**](../Models/BetaMessageBatch.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="betaMessageBatchesResults"></a>
# **betaMessageBatchesResults**
> File betaMessageBatchesResults(message\_batch\_id, anthropic-beta, anthropic-version, x-api-key)

Retrieve Message Batch results

    Streams the results of a Message Batch as a &#x60;.jsonl&#x60; file.  Each line in the file is a JSON object containing the result of a single request in the Message Batch. Results are not guaranteed to be in the same order as requests. Use the &#x60;custom_id&#x60; field to match results to requests.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **message\_batch\_id** | **String**| ID of the Message Batch. | [default to null] |
| **anthropic-beta** | **String**| Optional header to specify the beta version(s) you want to use.  To use multiple betas, use a comma separated list like &#x60;beta1,beta2&#x60; or specify the header multiple times for each beta. | [optional] [default to null] |
| **anthropic-version** | **String**| The version of the Anthropic API you want to use.  Read more about versioning and our version history [here](https://docs.anthropic.com/en/api/versioning). | [optional] [default to null] |
| **x-api-key** | **String**| Your unique API key for authentication.   This key is required in the header of all API requests, to authenticate your account and access Anthropic&#39;s services. Get your API key through the [Console](https://console.anthropic.com/settings/keys). Each key is scoped to a Workspace. | [optional] [default to null] |

### Return type

**File**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/x-jsonl, application/json

<a name="betaMessageBatchesResults_0"></a>
# **betaMessageBatchesResults_0**
> File betaMessageBatchesResults_0(message\_batch\_id, anthropic-beta, anthropic-version, x-api-key)

Retrieve Message Batch results

    Streams the results of a Message Batch as a &#x60;.jsonl&#x60; file.  Each line in the file is a JSON object containing the result of a single request in the Message Batch. Results are not guaranteed to be in the same order as requests. Use the &#x60;custom_id&#x60; field to match results to requests.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **message\_batch\_id** | **String**| ID of the Message Batch. | [default to null] |
| **anthropic-beta** | **String**| Optional header to specify the beta version(s) you want to use.  To use multiple betas, use a comma separated list like &#x60;beta1,beta2&#x60; or specify the header multiple times for each beta. | [optional] [default to null] |
| **anthropic-version** | **String**| The version of the Anthropic API you want to use.  Read more about versioning and our version history [here](https://docs.anthropic.com/en/api/versioning). | [optional] [default to null] |
| **x-api-key** | **String**| Your unique API key for authentication.   This key is required in the header of all API requests, to authenticate your account and access Anthropic&#39;s services. Get your API key through the [Console](https://console.anthropic.com/settings/keys). Each key is scoped to a Workspace. | [optional] [default to null] |

### Return type

**File**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/x-jsonl, application/json

<a name="betaMessageBatchesRetrieve"></a>
# **betaMessageBatchesRetrieve**
> BetaMessageBatch betaMessageBatchesRetrieve(message\_batch\_id, anthropic-beta, anthropic-version, x-api-key)

Retrieve a Message Batch

    This endpoint is idempotent and can be used to poll for Message Batch completion. To access the results of a Message Batch, make a request to the &#x60;results_url&#x60; field in the response.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **message\_batch\_id** | **String**| ID of the Message Batch. | [default to null] |
| **anthropic-beta** | **String**| Optional header to specify the beta version(s) you want to use.  To use multiple betas, use a comma separated list like &#x60;beta1,beta2&#x60; or specify the header multiple times for each beta. | [optional] [default to null] |
| **anthropic-version** | **String**| The version of the Anthropic API you want to use.  Read more about versioning and our version history [here](https://docs.anthropic.com/en/api/versioning). | [optional] [default to null] |
| **x-api-key** | **String**| Your unique API key for authentication.   This key is required in the header of all API requests, to authenticate your account and access Anthropic&#39;s services. Get your API key through the [Console](https://console.anthropic.com/settings/keys). Each key is scoped to a Workspace. | [optional] [default to null] |

### Return type

[**BetaMessageBatch**](../Models/BetaMessageBatch.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="betaMessageBatchesRetrieve_0"></a>
# **betaMessageBatchesRetrieve_0**
> BetaMessageBatch betaMessageBatchesRetrieve_0(message\_batch\_id, anthropic-beta, anthropic-version, x-api-key)

Retrieve a Message Batch

    This endpoint is idempotent and can be used to poll for Message Batch completion. To access the results of a Message Batch, make a request to the &#x60;results_url&#x60; field in the response.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **message\_batch\_id** | **String**| ID of the Message Batch. | [default to null] |
| **anthropic-beta** | **String**| Optional header to specify the beta version(s) you want to use.  To use multiple betas, use a comma separated list like &#x60;beta1,beta2&#x60; or specify the header multiple times for each beta. | [optional] [default to null] |
| **anthropic-version** | **String**| The version of the Anthropic API you want to use.  Read more about versioning and our version history [here](https://docs.anthropic.com/en/api/versioning). | [optional] [default to null] |
| **x-api-key** | **String**| Your unique API key for authentication.   This key is required in the header of all API requests, to authenticate your account and access Anthropic&#39;s services. Get your API key through the [Console](https://console.anthropic.com/settings/keys). Each key is scoped to a Workspace. | [optional] [default to null] |

### Return type

[**BetaMessageBatch**](../Models/BetaMessageBatch.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

