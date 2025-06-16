# RealtimeSession_turn_detection
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **type** | **String** | Type of turn detection.  | [optional] [default to server_vad] |
| **eagerness** | **String** | Used only for &#x60;semantic_vad&#x60; mode. The eagerness of the model to respond. &#x60;low&#x60; will wait longer for the user to continue speaking, &#x60;high&#x60; will respond more quickly. &#x60;auto&#x60; is the default and is equivalent to &#x60;medium&#x60;.  | [optional] [default to auto] |
| **threshold** | **BigDecimal** | Used only for &#x60;server_vad&#x60; mode. Activation threshold for VAD (0.0 to 1.0), this defaults to 0.5. A  higher threshold will require louder audio to activate the model, and  thus might perform better in noisy environments.  | [optional] [default to null] |
| **prefix\_padding\_ms** | **Integer** | Used only for &#x60;server_vad&#x60; mode. Amount of audio to include before the VAD detected speech (in  milliseconds). Defaults to 300ms.  | [optional] [default to null] |
| **silence\_duration\_ms** | **Integer** | Used only for &#x60;server_vad&#x60; mode. Duration of silence to detect speech stop (in milliseconds). Defaults  to 500ms. With shorter values the model will respond more quickly,  but may jump in on short pauses from the user.  | [optional] [default to null] |
| **create\_response** | **Boolean** | Whether or not to automatically generate a response when a VAD stop event occurs.  | [optional] [default to true] |
| **interrupt\_response** | **Boolean** | Whether or not to automatically interrupt any ongoing response with output to the default conversation (i.e. &#x60;conversation&#x60; of &#x60;auto&#x60;) when a VAD start event occurs.  | [optional] [default to true] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

