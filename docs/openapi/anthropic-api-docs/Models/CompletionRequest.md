# CompletionRequest
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **model** | [**Model**](Model.md) |  | [default to null] |
| **prompt** | **String** | The prompt that you want Claude to complete.  For proper response generation you will need to format your prompt using alternating &#x60;\\n\\nHuman:&#x60; and &#x60;\\n\\nAssistant:&#x60; conversational turns. For example:  &#x60;&#x60;&#x60; \&quot;\\n\\nHuman: {userQuestion}\\n\\nAssistant:\&quot; &#x60;&#x60;&#x60;  See [prompt validation](https://docs.anthropic.com/en/api/prompt-validation) and our guide to [prompt design](https://docs.anthropic.com/en/docs/intro-to-prompting) for more details. | [default to null] |
| **max\_tokens\_to\_sample** | **Integer** | The maximum number of tokens to generate before stopping.  Note that our models may stop _before_ reaching this maximum. This parameter only specifies the absolute maximum number of tokens to generate. | [default to null] |
| **stop\_sequences** | **List** | Sequences that will cause the model to stop generating.  Our models stop on &#x60;\&quot;\\n\\nHuman:\&quot;&#x60;, and may include additional built-in stop sequences in the future. By providing the stop_sequences parameter, you may include additional strings that will cause the model to stop generating. | [optional] [default to null] |
| **temperature** | **BigDecimal** | Amount of randomness injected into the response.  Defaults to &#x60;1.0&#x60;. Ranges from &#x60;0.0&#x60; to &#x60;1.0&#x60;. Use &#x60;temperature&#x60; closer to &#x60;0.0&#x60; for analytical / multiple choice, and closer to &#x60;1.0&#x60; for creative and generative tasks.  Note that even with &#x60;temperature&#x60; of &#x60;0.0&#x60;, the results will not be fully deterministic. | [optional] [default to null] |
| **top\_p** | **BigDecimal** | Use nucleus sampling.  In nucleus sampling, we compute the cumulative distribution over all the options for each subsequent token in decreasing probability order and cut it off once it reaches a particular probability specified by &#x60;top_p&#x60;. You should either alter &#x60;temperature&#x60; or &#x60;top_p&#x60;, but not both.  Recommended for advanced use cases only. You usually only need to use &#x60;temperature&#x60;. | [optional] [default to null] |
| **top\_k** | **Integer** | Only sample from the top K options for each subsequent token.  Used to remove \&quot;long tail\&quot; low probability responses. [Learn more technical details here](https://towardsdatascience.com/how-to-sample-from-language-models-682bceb97277).  Recommended for advanced use cases only. You usually only need to use &#x60;temperature&#x60;. | [optional] [default to null] |
| **metadata** | [**Metadata**](Metadata.md) | An object describing metadata about the request. | [optional] [default to null] |
| **stream** | **Boolean** | Whether to incrementally stream the response using server-sent events.  See [streaming](https://docs.anthropic.com/en/api/streaming) for details. | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

