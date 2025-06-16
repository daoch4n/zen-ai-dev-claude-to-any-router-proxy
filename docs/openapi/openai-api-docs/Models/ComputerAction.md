# ComputerAction
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **type** | **String** | Specifies the event type. For a click action, this property is  always set to &#x60;click&#x60;.  | [default to click] |
| **button** | **String** | Indicates which mouse button was pressed during the click. One of &#x60;left&#x60;, &#x60;right&#x60;, &#x60;wheel&#x60;, &#x60;back&#x60;, or &#x60;forward&#x60;.  | [default to null] |
| **x** | **Integer** | The x-coordinate where the scroll occurred.  | [default to null] |
| **y** | **Integer** | The y-coordinate where the scroll occurred.  | [default to null] |
| **path** | [**List**](Coordinate.md) | An array of coordinates representing the path of the drag action. Coordinates will appear as an array of objects, eg &#x60;&#x60;&#x60; [   { x: 100, y: 200 },   { x: 200, y: 300 } ] &#x60;&#x60;&#x60;  | [default to null] |
| **keys** | **List** | The combination of keys the model is requesting to be pressed. This is an array of strings, each representing a key.  | [default to null] |
| **scroll\_x** | **Integer** | The horizontal scroll distance.  | [default to null] |
| **scroll\_y** | **Integer** | The vertical scroll distance.  | [default to null] |
| **text** | **String** | The text to type.  | [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

