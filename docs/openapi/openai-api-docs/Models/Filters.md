# Filters
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **type** | **String** | Specifies the comparison operator: &#x60;eq&#x60;, &#x60;ne&#x60;, &#x60;gt&#x60;, &#x60;gte&#x60;, &#x60;lt&#x60;, &#x60;lte&#x60;. - &#x60;eq&#x60;: equals - &#x60;ne&#x60;: not equal - &#x60;gt&#x60;: greater than - &#x60;gte&#x60;: greater than or equal - &#x60;lt&#x60;: less than - &#x60;lte&#x60;: less than or equal  | [default to eq] |
| **key** | **String** | The key to compare against the value. | [default to null] |
| **value** | [**ComparisonFilter_value**](ComparisonFilter_value.md) |  | [default to null] |
| **filters** | [**List**](CompoundFilter_filters_inner.md) | Array of filters to combine. Items can be &#x60;ComparisonFilter&#x60; or &#x60;CompoundFilter&#x60;. | [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

