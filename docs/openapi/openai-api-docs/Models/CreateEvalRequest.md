# CreateEvalRequest
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **name** | **String** | The name of the evaluation. | [optional] [default to null] |
| **metadata** | **Map** | Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard.   Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.  | [optional] [default to null] |
| **data\_source\_config** | [**CreateEvalRequest_data_source_config**](CreateEvalRequest_data_source_config.md) |  | [default to null] |
| **testing\_criteria** | [**List**](CreateEvalRequest_testing_criteria_inner.md) | A list of graders for all eval runs in this group. | [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

