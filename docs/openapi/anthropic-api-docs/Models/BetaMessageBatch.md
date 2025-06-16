# BetaMessageBatch
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **id** | **String** | Unique object identifier.  The format and length of IDs may change over time. | [default to null] |
| **type** | **String** | Object type.  For Message Batches, this is always &#x60;\&quot;message_batch\&quot;&#x60;. | [default to message_batch] |
| **processing\_status** | **String** | Processing status of the Message Batch. | [default to null] |
| **request\_counts** | [**BetaRequestCounts**](BetaRequestCounts.md) | Tallies requests within the Message Batch, categorized by their status.  Requests start as &#x60;processing&#x60; and move to one of the other statuses only once processing of the entire batch ends. The sum of all values always matches the total number of requests in the batch. | [default to null] |
| **ended\_at** | **Date** |  | [default to null] |
| **created\_at** | **Date** | RFC 3339 datetime string representing the time at which the Message Batch was created. | [default to null] |
| **expires\_at** | **Date** | RFC 3339 datetime string representing the time at which the Message Batch will expire and end processing, which is 24 hours after creation. | [default to null] |
| **archived\_at** | **Date** |  | [default to null] |
| **cancel\_initiated\_at** | **Date** |  | [default to null] |
| **results\_url** | **String** |  | [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

