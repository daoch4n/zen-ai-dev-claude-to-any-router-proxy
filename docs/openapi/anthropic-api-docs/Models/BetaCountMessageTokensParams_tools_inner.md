# BetaCountMessageTokensParams_tools_inner
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **type** | **String** |  | [default to null] |
| **description** | **String** | Description of what this tool does.  Tool descriptions should be as detailed as possible. The more information that the model has about what the tool is and how to use it, the better it will perform. You can use natural language descriptions to reinforce important aspects of the tool input JSON schema. | [optional] [default to null] |
| **name** | **String** | Name of the tool.  This is how the tool will be called by the model and in tool_use blocks. | [default to null] |
| **input\_schema** | [**BetaInputSchema**](BetaInputSchema.md) | [JSON schema](https://json-schema.org/) for this tool&#39;s input.  This defines the shape of the &#x60;input&#x60; that your tool accepts and that the model will produce. | [default to null] |
| **cache\_control** | [**BetaCacheControlEphemeral**](BetaCacheControlEphemeral.md) |  | [optional] [default to null] |
| **display\_height\_px** | **Integer** | The height of the display in pixels. | [default to null] |
| **display\_width\_px** | **Integer** | The width of the display in pixels. | [default to null] |
| **display\_number** | **Integer** |  | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

