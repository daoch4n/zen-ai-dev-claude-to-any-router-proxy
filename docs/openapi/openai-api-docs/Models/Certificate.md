# Certificate
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **object** | **String** | The object type.  - If creating, updating, or getting a specific certificate, the object type is &#x60;certificate&#x60;. - If listing, activating, or deactivating certificates for the organization, the object type is &#x60;organization.certificate&#x60;. - If listing, activating, or deactivating certificates for a project, the object type is &#x60;organization.project.certificate&#x60;.  | [default to null] |
| **id** | **String** | The identifier, which can be referenced in API endpoints | [default to null] |
| **name** | **String** | The name of the certificate. | [default to null] |
| **created\_at** | **Integer** | The Unix timestamp (in seconds) of when the certificate was uploaded. | [default to null] |
| **certificate\_details** | [**Certificate_certificate_details**](Certificate_certificate_details.md) |  | [default to null] |
| **active** | **Boolean** | Whether the certificate is currently active at the specified scope. Not returned when getting details for a specific certificate. | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

