# MessageDeltaEvent
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **type** | **String** |  | [default to message_delta] |
| **delta** | [**MessageDelta**](MessageDelta.md) |  | [default to null] |
| **usage** | [**MessageDeltaUsage**](MessageDeltaUsage.md) | Billing and rate-limit usage.  Anthropic&#39;s API bills and rate-limits by token counts, as tokens represent the underlying cost to our systems.  Under the hood, the API transforms requests into a format suitable for the model. The model&#39;s output then goes through a parsing stage before becoming an API response. As a result, the token counts in &#x60;usage&#x60; will not match one-to-one with the exact visible content of an API request or response.  For example, &#x60;output_tokens&#x60; will be non-zero, even for an empty string response from Claude. | [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

