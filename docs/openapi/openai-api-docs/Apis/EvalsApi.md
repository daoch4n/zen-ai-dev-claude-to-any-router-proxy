# EvalsApi

All URIs are relative to *https://api.openai.com/v1*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**cancelEvalRun**](EvalsApi.md#cancelEvalRun) | **POST** /evals/{eval_id}/runs/{run_id} | Cancel an ongoing evaluation run.  |
| [**createEval**](EvalsApi.md#createEval) | **POST** /evals | Create the structure of an evaluation that can be used to test a model&#39;s performance. An evaluation is a set of testing criteria and a datasource. After creating an evaluation, you can run it on different models and model parameters. We support several types of graders and datasources. For more information, see the [Evals guide](/docs/guides/evals).  |
| [**createEvalRun**](EvalsApi.md#createEvalRun) | **POST** /evals/{eval_id}/runs | Create a new evaluation run. This is the endpoint that will kick off grading.  |
| [**deleteEval**](EvalsApi.md#deleteEval) | **DELETE** /evals/{eval_id} | Delete an evaluation.  |
| [**deleteEvalRun**](EvalsApi.md#deleteEvalRun) | **DELETE** /evals/{eval_id}/runs/{run_id} | Delete an eval run.  |
| [**getEval**](EvalsApi.md#getEval) | **GET** /evals/{eval_id} | Get an evaluation by ID.  |
| [**getEvalRun**](EvalsApi.md#getEvalRun) | **GET** /evals/{eval_id}/runs/{run_id} | Get an evaluation run by ID.  |
| [**getEvalRunOutputItem**](EvalsApi.md#getEvalRunOutputItem) | **GET** /evals/{eval_id}/runs/{run_id}/output_items/{output_item_id} | Get an evaluation run output item by ID.  |
| [**getEvalRunOutputItems**](EvalsApi.md#getEvalRunOutputItems) | **GET** /evals/{eval_id}/runs/{run_id}/output_items | Get a list of output items for an evaluation run.  |
| [**getEvalRuns**](EvalsApi.md#getEvalRuns) | **GET** /evals/{eval_id}/runs | Get a list of runs for an evaluation.  |
| [**listEvals**](EvalsApi.md#listEvals) | **GET** /evals | List evaluations for a project.  |
| [**updateEval**](EvalsApi.md#updateEval) | **POST** /evals/{eval_id} | Update certain properties of an evaluation.  |


<a name="cancelEvalRun"></a>
# **cancelEvalRun**
> EvalRun cancelEvalRun(eval\_id, run\_id)

Cancel an ongoing evaluation run. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **eval\_id** | **String**| The ID of the evaluation whose run you want to cancel. | [default to null] |
| **run\_id** | **String**| The ID of the run to cancel. | [default to null] |

### Return type

[**EvalRun**](../Models/EvalRun.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="createEval"></a>
# **createEval**
> Eval createEval(CreateEvalRequest)

Create the structure of an evaluation that can be used to test a model&#39;s performance. An evaluation is a set of testing criteria and a datasource. After creating an evaluation, you can run it on different models and model parameters. We support several types of graders and datasources. For more information, see the [Evals guide](/docs/guides/evals). 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **CreateEvalRequest** | [**CreateEvalRequest**](../Models/CreateEvalRequest.md)|  | |

### Return type

[**Eval**](../Models/Eval.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="createEvalRun"></a>
# **createEvalRun**
> EvalRun createEvalRun(eval\_id, CreateEvalRunRequest)

Create a new evaluation run. This is the endpoint that will kick off grading. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **eval\_id** | **String**| The ID of the evaluation to create a run for. | [default to null] |
| **CreateEvalRunRequest** | [**CreateEvalRunRequest**](../Models/CreateEvalRunRequest.md)|  | |

### Return type

[**EvalRun**](../Models/EvalRun.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="deleteEval"></a>
# **deleteEval**
> deleteEval_200_response deleteEval(eval\_id)

Delete an evaluation. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **eval\_id** | **String**| The ID of the evaluation to delete. | [default to null] |

### Return type

[**deleteEval_200_response**](../Models/deleteEval_200_response.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="deleteEvalRun"></a>
# **deleteEvalRun**
> deleteEvalRun_200_response deleteEvalRun(eval\_id, run\_id)

Delete an eval run. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **eval\_id** | **String**| The ID of the evaluation to delete the run from. | [default to null] |
| **run\_id** | **String**| The ID of the run to delete. | [default to null] |

### Return type

[**deleteEvalRun_200_response**](../Models/deleteEvalRun_200_response.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getEval"></a>
# **getEval**
> Eval getEval(eval\_id)

Get an evaluation by ID. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **eval\_id** | **String**| The ID of the evaluation to retrieve. | [default to null] |

### Return type

[**Eval**](../Models/Eval.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getEvalRun"></a>
# **getEvalRun**
> EvalRun getEvalRun(eval\_id, run\_id)

Get an evaluation run by ID. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **eval\_id** | **String**| The ID of the evaluation to retrieve runs for. | [default to null] |
| **run\_id** | **String**| The ID of the run to retrieve. | [default to null] |

### Return type

[**EvalRun**](../Models/EvalRun.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getEvalRunOutputItem"></a>
# **getEvalRunOutputItem**
> EvalRunOutputItem getEvalRunOutputItem(eval\_id, run\_id, output\_item\_id)

Get an evaluation run output item by ID. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **eval\_id** | **String**| The ID of the evaluation to retrieve runs for. | [default to null] |
| **run\_id** | **String**| The ID of the run to retrieve. | [default to null] |
| **output\_item\_id** | **String**| The ID of the output item to retrieve. | [default to null] |

### Return type

[**EvalRunOutputItem**](../Models/EvalRunOutputItem.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getEvalRunOutputItems"></a>
# **getEvalRunOutputItems**
> EvalRunOutputItemList getEvalRunOutputItems(eval\_id, run\_id, after, limit, status, order)

Get a list of output items for an evaluation run. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **eval\_id** | **String**| The ID of the evaluation to retrieve runs for. | [default to null] |
| **run\_id** | **String**| The ID of the run to retrieve output items for. | [default to null] |
| **after** | **String**| Identifier for the last output item from the previous pagination request. | [optional] [default to null] |
| **limit** | **Integer**| Number of output items to retrieve. | [optional] [default to 20] |
| **status** | **String**| Filter output items by status. Use &#x60;failed&#x60; to filter by failed output items or &#x60;pass&#x60; to filter by passed output items.  | [optional] [default to null] [enum: fail, pass] |
| **order** | **String**| Sort order for output items by timestamp. Use &#x60;asc&#x60; for ascending order or &#x60;desc&#x60; for descending order. Defaults to &#x60;asc&#x60;. | [optional] [default to asc] [enum: asc, desc] |

### Return type

[**EvalRunOutputItemList**](../Models/EvalRunOutputItemList.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getEvalRuns"></a>
# **getEvalRuns**
> EvalRunList getEvalRuns(eval\_id, after, limit, order, status)

Get a list of runs for an evaluation. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **eval\_id** | **String**| The ID of the evaluation to retrieve runs for. | [default to null] |
| **after** | **String**| Identifier for the last run from the previous pagination request. | [optional] [default to null] |
| **limit** | **Integer**| Number of runs to retrieve. | [optional] [default to 20] |
| **order** | **String**| Sort order for runs by timestamp. Use &#x60;asc&#x60; for ascending order or &#x60;desc&#x60; for descending order. Defaults to &#x60;asc&#x60;. | [optional] [default to asc] [enum: asc, desc] |
| **status** | **String**| Filter runs by status. One of &#x60;queued&#x60; | &#x60;in_progress&#x60; | &#x60;failed&#x60; | &#x60;completed&#x60; | &#x60;canceled&#x60;. | [optional] [default to null] [enum: queued, in_progress, completed, canceled, failed] |

### Return type

[**EvalRunList**](../Models/EvalRunList.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="listEvals"></a>
# **listEvals**
> EvalList listEvals(after, limit, order, order\_by)

List evaluations for a project. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **after** | **String**| Identifier for the last eval from the previous pagination request. | [optional] [default to null] |
| **limit** | **Integer**| Number of evals to retrieve. | [optional] [default to 20] |
| **order** | **String**| Sort order for evals by timestamp. Use &#x60;asc&#x60; for ascending order or &#x60;desc&#x60; for descending order. | [optional] [default to asc] [enum: asc, desc] |
| **order\_by** | **String**| Evals can be ordered by creation time or last updated time. Use &#x60;created_at&#x60; for creation time or &#x60;updated_at&#x60; for last updated time.  | [optional] [default to created_at] [enum: created_at, updated_at] |

### Return type

[**EvalList**](../Models/EvalList.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="updateEval"></a>
# **updateEval**
> Eval updateEval(eval\_id, updateEval\_request)

Update certain properties of an evaluation. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **eval\_id** | **String**| The ID of the evaluation to update. | [default to null] |
| **updateEval\_request** | [**updateEval_request**](../Models/updateEval_request.md)| Request to update an evaluation | |

### Return type

[**Eval**](../Models/Eval.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

