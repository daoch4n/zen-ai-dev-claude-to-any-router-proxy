# ResponseStreamEvent
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **type** | **String** | The type of the event. Always &#x60;response.audio.delta&#x60;.  | [default to null] |
| **delta** | **String** | The text delta that was added.  | [default to null] |
| **output\_index** | **Integer** | The index of the output item that the web search call is associated with.  | [default to null] |
| **code** | **String** | The error code.  | [default to null] |
| **code\_interpreter\_call** | [**CodeInterpreterToolCall**](CodeInterpreterToolCall.md) |  | [default to null] |
| **response** | [**Response**](Response.md) |  | [default to null] |
| **item\_id** | **String** | Unique ID for the output item associated with the web search call.  | [default to null] |
| **content\_index** | **Integer** | The index of the content part that the text content is finalized.  | [default to null] |
| **part** | [**ResponseReasoningSummaryPartDoneEvent_part**](ResponseReasoningSummaryPartDoneEvent_part.md) |  | [default to null] |
| **message** | **String** | The error message.  | [default to null] |
| **param** | **String** | The error parameter.  | [default to null] |
| **arguments** | **String** | The function-call arguments. | [default to null] |
| **item** | [**OutputItem**](OutputItem.md) |  | [default to null] |
| **summary\_index** | **Integer** | The index of the summary part within the reasoning summary.  | [default to null] |
| **text** | **String** | The text content that is finalized.  | [default to null] |
| **refusal** | **String** | The refusal text that is finalized.  | [default to null] |
| **annotation\_index** | **Integer** | The index of the annotation that was added.  | [default to null] |
| **annotation** | [**Annotation**](Annotation.md) |  | [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

