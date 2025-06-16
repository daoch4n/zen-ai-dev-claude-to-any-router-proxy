# ChatCompletionRequest
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **messages** | [**List**](ChatMessage.md) | A list of messages comprising the conversation so far | [default to null] |
| **model** | **String** | ID of the model to use. If omitted, uses user&#39;s default. Format: provider/model-name (e.g., \&quot;openai/gpt-4o\&quot;)  | [optional] [default to null] |
| **models** | **List** | List of models to route between (OpenRouter-specific) | [optional] [default to null] |
| **route** | **String** | Routing strategy (OpenRouter-specific) | [optional] [default to null] |
| **provider** | [**ProviderPreferences**](ProviderPreferences.md) |  | [optional] [default to null] |
| **transforms** | **List** | List of prompt transforms to apply (OpenRouter-specific) | [optional] [default to null] |
| **max\_tokens** | **Integer** | Maximum number of tokens to generate | [optional] [default to null] |
| **temperature** | **BigDecimal** | Sampling temperature between 0 and 2 | [optional] [default to null] |
| **top\_p** | **BigDecimal** | Nucleus sampling parameter | [optional] [default to null] |
| **top\_k** | **Integer** | Top-k sampling parameter (not available for OpenAI models) | [optional] [default to null] |
| **frequency\_penalty** | **BigDecimal** | Frequency penalty parameter | [optional] [default to null] |
| **presence\_penalty** | **BigDecimal** | Presence penalty parameter | [optional] [default to null] |
| **repetition\_penalty** | **BigDecimal** | Repetition penalty parameter | [optional] [default to null] |
| **stop** | [**ChatCompletionRequest_stop**](ChatCompletionRequest_stop.md) |  | [optional] [default to null] |
| **stream** | **Boolean** | Whether to stream back partial progress | [optional] [default to false] |
| **tools** | [**List**](Tool.md) | List of tools the model may call | [optional] [default to null] |
| **tool\_choice** | [**ToolChoice**](ToolChoice.md) |  | [optional] [default to null] |
| **response\_format** | [**ChatCompletionRequest_response_format**](ChatCompletionRequest_response_format.md) |  | [optional] [default to null] |
| **seed** | **Integer** | Random seed for deterministic generation | [optional] [default to null] |
| **logit\_bias** | **Map** | Token biases | [optional] [default to null] |
| **top\_logprobs** | **Integer** | Number of most likely tokens to return | [optional] [default to null] |
| **min\_p** | **BigDecimal** | Minimum probability threshold | [optional] [default to null] |
| **top\_a** | **BigDecimal** | Top-a sampling parameter | [optional] [default to null] |
| **user** | **String** | Unique identifier for end-user | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

