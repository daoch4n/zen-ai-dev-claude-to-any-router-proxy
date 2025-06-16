# TeamAddMemberResponse
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **team\_alias** | **String** |  | [optional] [default to null] |
| **team\_id** | **String** |  | [default to null] |
| **organization\_id** | **String** |  | [optional] [default to null] |
| **admins** | [**List**](AnyType.md) |  | [optional] [default to []] |
| **members** | [**List**](AnyType.md) |  | [optional] [default to []] |
| **members\_with\_roles** | [**List**](Member.md) |  | [optional] [default to []] |
| **team\_member\_permissions** | **List** |  | [optional] [default to null] |
| **metadata** | [**Object**](.md) |  | [optional] [default to null] |
| **tpm\_limit** | **Integer** |  | [optional] [default to null] |
| **rpm\_limit** | **Integer** |  | [optional] [default to null] |
| **max\_budget** | **BigDecimal** |  | [optional] [default to null] |
| **budget\_duration** | **String** |  | [optional] [default to null] |
| **models** | [**List**](AnyType.md) |  | [optional] [default to []] |
| **blocked** | **Boolean** |  | [optional] [default to false] |
| **spend** | **BigDecimal** |  | [optional] [default to null] |
| **max\_parallel\_requests** | **Integer** |  | [optional] [default to null] |
| **budget\_reset\_at** | **Date** |  | [optional] [default to null] |
| **model\_id** | **Integer** |  | [optional] [default to null] |
| **litellm\_model\_table** | [**LiteLLM_ModelTable**](LiteLLM_ModelTable.md) |  | [optional] [default to null] |
| **object\_permission** | [**LiteLLM_ObjectPermissionTable**](LiteLLM_ObjectPermissionTable.md) |  | [optional] [default to null] |
| **updated\_at** | **Date** |  | [optional] [default to null] |
| **created\_at** | **Date** |  | [optional] [default to null] |
| **object\_permission\_id** | **String** |  | [optional] [default to null] |
| **updated\_users** | [**List**](LiteLLM_UserTable.md) |  | [default to null] |
| **updated\_team\_memberships** | [**List**](LiteLLM_TeamMembership.md) |  | [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

