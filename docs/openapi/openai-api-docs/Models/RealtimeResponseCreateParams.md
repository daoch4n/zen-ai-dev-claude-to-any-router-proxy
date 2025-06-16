# RealtimeResponseCreateParams
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **modalities** | **List** | The set of modalities the model can respond with. To disable audio, set this to [\&quot;text\&quot;].  | [optional] [default to null] |
| **instructions** | **String** | The default system instructions (i.e. system message) prepended to model  calls. This field allows the client to guide the model on desired  responses. The model can be instructed on response content and format,  (e.g. \&quot;be extremely succinct\&quot;, \&quot;act friendly\&quot;, \&quot;here are examples of good  responses\&quot;) and on audio behavior (e.g. \&quot;talk quickly\&quot;, \&quot;inject emotion  into your voice\&quot;, \&quot;laugh frequently\&quot;). The instructions are not guaranteed  to be followed by the model, but they provide guidance to the model on the  desired behavior.  Note that the server sets default instructions which will be used if this  field is not set and are visible in the &#x60;session.created&#x60; event at the  start of the session.  | [optional] [default to null] |
| **voice** | [**VoiceIdsShared**](VoiceIdsShared.md) |  | [optional] [default to null] |
| **output\_audio\_format** | **String** | The format of output audio. Options are &#x60;pcm16&#x60;, &#x60;g711_ulaw&#x60;, or &#x60;g711_alaw&#x60;.  | [optional] [default to null] |
| **tools** | [**List**](RealtimeResponseCreateParams_tools_inner.md) | Tools (functions) available to the model. | [optional] [default to null] |
| **tool\_choice** | **String** | How the model chooses tools. Options are &#x60;auto&#x60;, &#x60;none&#x60;, &#x60;required&#x60;, or  specify a function, like &#x60;{\&quot;type\&quot;: \&quot;function\&quot;, \&quot;function\&quot;: {\&quot;name\&quot;: \&quot;my_function\&quot;}}&#x60;.  | [optional] [default to null] |
| **temperature** | **BigDecimal** | Sampling temperature for the model, limited to [0.6, 1.2]. Defaults to 0.8.  | [optional] [default to null] |
| **max\_response\_output\_tokens** | [**RealtimeResponseCreateParams_max_response_output_tokens**](RealtimeResponseCreateParams_max_response_output_tokens.md) |  | [optional] [default to null] |
| **conversation** | [**RealtimeResponseCreateParams_conversation**](RealtimeResponseCreateParams_conversation.md) |  | [optional] [default to null] |
| **metadata** | **Map** | Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard.   Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.  | [optional] [default to null] |
| **input** | [**List**](RealtimeConversationItemWithReference.md) | Input items to include in the prompt for the model. Using this field creates a new context for this Response instead of using the default conversation. An empty array &#x60;[]&#x60; will clear the context for this Response. Note that this can include references to items from the default conversation.  | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

