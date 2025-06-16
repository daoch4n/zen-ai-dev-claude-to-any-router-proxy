# AdminApiKey
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **object** | **String** | The object type, which is always &#x60;organization.admin_api_key&#x60; | [default to null] |
| **id** | **String** | The identifier, which can be referenced in API endpoints | [default to null] |
| **name** | **String** | The name of the API key | [default to null] |
| **redacted\_value** | **String** | The redacted value of the API key | [default to null] |
| **value** | **String** | The value of the API key. Only shown on create. | [optional] [default to null] |
| **created\_at** | **Long** | The Unix timestamp (in seconds) of when the API key was created | [default to null] |
| **last\_used\_at** | **Long** | The Unix timestamp (in seconds) of when the API key was last used | [default to null] |
| **owner** | [**AdminApiKey_owner**](AdminApiKey_owner.md) |  | [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

