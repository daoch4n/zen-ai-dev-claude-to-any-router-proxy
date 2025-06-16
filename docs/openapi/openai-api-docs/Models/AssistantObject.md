# AssistantObject
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **id** | **String** | The identifier, which can be referenced in API endpoints. | [default to null] |
| **object** | **String** | The object type, which is always &#x60;assistant&#x60;. | [default to null] |
| **created\_at** | **Integer** | The Unix timestamp (in seconds) for when the assistant was created. | [default to null] |
| **name** | **String** | The name of the assistant. The maximum length is 256 characters.  | [default to null] |
| **description** | **String** | The description of the assistant. The maximum length is 512 characters.  | [default to null] |
| **model** | **String** | ID of the model to use. You can use the [List models](/docs/api-reference/models/list) API to see all of your available models, or see our [Model overview](/docs/models) for descriptions of them.  | [default to null] |
| **instructions** | **String** | The system instructions that the assistant uses. The maximum length is 256,000 characters.  | [default to null] |
| **tools** | [**List**](AssistantObject_tools_inner.md) | A list of tool enabled on the assistant. There can be a maximum of 128 tools per assistant. Tools can be of types &#x60;code_interpreter&#x60;, &#x60;file_search&#x60;, or &#x60;function&#x60;.  | [default to []] |
| **tool\_resources** | [**AssistantObject_tool_resources**](AssistantObject_tool_resources.md) |  | [optional] [default to null] |
| **metadata** | **Map** | Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard.   Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.  | [default to null] |
| **temperature** | **BigDecimal** | What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.  | [optional] [default to 1] |
| **top\_p** | **BigDecimal** | An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.  We generally recommend altering this or temperature but not both.  | [optional] [default to 1] |
| **response\_format** | [**AssistantsApiResponseFormatOption**](AssistantsApiResponseFormatOption.md) |  | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

