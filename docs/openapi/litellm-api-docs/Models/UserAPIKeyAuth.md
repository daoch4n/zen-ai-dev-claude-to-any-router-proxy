# UserAPIKeyAuth
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **token** | **String** |  | [optional] [default to null] |
| **key\_name** | **String** |  | [optional] [default to null] |
| **key\_alias** | **String** |  | [optional] [default to null] |
| **spend** | **BigDecimal** |  | [optional] [default to 0.0] |
| **max\_budget** | **BigDecimal** |  | [optional] [default to null] |
| **expires** | [**Expires**](Expires.md) |  | [optional] [default to null] |
| **models** | [**List**](AnyType.md) |  | [optional] [default to []] |
| **aliases** | [**Object**](.md) |  | [optional] [default to {}] |
| **config** | [**Object**](.md) |  | [optional] [default to {}] |
| **user\_id** | **String** |  | [optional] [default to null] |
| **team\_id** | **String** |  | [optional] [default to null] |
| **max\_parallel\_requests** | **Integer** |  | [optional] [default to null] |
| **metadata** | [**Object**](.md) |  | [optional] [default to {}] |
| **tpm\_limit** | **Integer** |  | [optional] [default to null] |
| **rpm\_limit** | **Integer** |  | [optional] [default to null] |
| **budget\_duration** | **String** |  | [optional] [default to null] |
| **budget\_reset\_at** | **Date** |  | [optional] [default to null] |
| **allowed\_cache\_controls** | [**List**](AnyType.md) |  | [optional] [default to null] |
| **allowed\_routes** | [**List**](AnyType.md) |  | [optional] [default to null] |
| **permissions** | [**Object**](.md) |  | [optional] [default to {}] |
| **model\_spend** | [**Object**](.md) |  | [optional] [default to {}] |
| **model\_max\_budget** | [**Object**](.md) |  | [optional] [default to {}] |
| **soft\_budget\_cooldown** | **Boolean** |  | [optional] [default to false] |
| **blocked** | **Boolean** |  | [optional] [default to null] |
| **litellm\_budget\_table** | [**Object**](.md) |  | [optional] [default to null] |
| **org\_id** | **String** |  | [optional] [default to null] |
| **created\_at** | **Date** |  | [optional] [default to null] |
| **created\_by** | **String** |  | [optional] [default to null] |
| **updated\_at** | **Date** |  | [optional] [default to null] |
| **updated\_by** | **String** |  | [optional] [default to null] |
| **object\_permission\_id** | **String** |  | [optional] [default to null] |
| **object\_permission** | [**LiteLLM_ObjectPermissionTable**](LiteLLM_ObjectPermissionTable.md) |  | [optional] [default to null] |
| **team\_spend** | **BigDecimal** |  | [optional] [default to null] |
| **team\_alias** | **String** |  | [optional] [default to null] |
| **team\_tpm\_limit** | **Integer** |  | [optional] [default to null] |
| **team\_rpm\_limit** | **Integer** |  | [optional] [default to null] |
| **team\_max\_budget** | **BigDecimal** |  | [optional] [default to null] |
| **team\_models** | [**List**](AnyType.md) |  | [optional] [default to []] |
| **team\_blocked** | **Boolean** |  | [optional] [default to false] |
| **soft\_budget** | **BigDecimal** |  | [optional] [default to null] |
| **team\_model\_aliases** | [**Object**](.md) |  | [optional] [default to null] |
| **team\_member\_spend** | **BigDecimal** |  | [optional] [default to null] |
| **team\_member** | [**Member**](Member.md) |  | [optional] [default to null] |
| **team\_metadata** | [**Object**](.md) |  | [optional] [default to null] |
| **end\_user\_id** | **String** |  | [optional] [default to null] |
| **end\_user\_tpm\_limit** | **Integer** |  | [optional] [default to null] |
| **end\_user\_rpm\_limit** | **Integer** |  | [optional] [default to null] |
| **end\_user\_max\_budget** | **BigDecimal** |  | [optional] [default to null] |
| **last\_refreshed\_at** | **BigDecimal** |  | [optional] [default to null] |
| **api\_key** | **String** |  | [optional] [default to null] |
| **user\_role** | [**LitellmUserRoles**](LitellmUserRoles.md) |  | [optional] [default to null] |
| **allowed\_model\_region** | **String** |  | [optional] [default to null] |
| **parent\_otel\_span** | [**anyOf&lt;&gt;**](anyOf&lt;&gt;.md) |  | [optional] [default to null] |
| **rpm\_limit\_per\_model** | **Map** |  | [optional] [default to null] |
| **tpm\_limit\_per\_model** | **Map** |  | [optional] [default to null] |
| **user\_tpm\_limit** | **Integer** |  | [optional] [default to null] |
| **user\_rpm\_limit** | **Integer** |  | [optional] [default to null] |
| **user\_email** | **String** |  | [optional] [default to null] |
| **request\_route** | **String** |  | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

