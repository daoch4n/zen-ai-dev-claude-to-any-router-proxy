# OAuthAPIApi

All URIs are relative to *https://api.anthropic.com*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**authorize**](OAuthAPIApi.md#authorize) | **GET** /oauth2/auth | OAuth authorization endpoint |
| [**token**](OAuthAPIApi.md#token) | **POST** /oauth2/token | OAuth token endpoint |


<a name="authorize"></a>
# **authorize**
> authorize(client\_id, redirect\_uri, response\_type, scope, state, code\_challenge, code\_challenge\_method)

OAuth authorization endpoint

    Initiates the OAuth authorization flow. Users are redirected to this endpoint to grant permissions. Supports PKCE (Proof Key for Code Exchange) for enhanced security. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **client\_id** | **String**| The client identifier for Claude Code CLI | [default to null] |
| **redirect\_uri** | **URI**| Redirect URI after authorization | [default to null] |
| **response\_type** | **String**| OAuth response type | [default to null] [enum: code] |
| **scope** | **String**| Requested permissions | [default to null] |
| **state** | **String**| Random state for CSRF protection | [default to null] |
| **code\_challenge** | **String**| PKCE code challenge | [optional] [default to null] |
| **code\_challenge\_method** | **String**| PKCE code challenge method | [optional] [default to null] [enum: S256] |

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="token"></a>
# **token**
> TokenResponse token(grant\_type, client\_id, client\_secret, code, redirect\_uri, code\_verifier, refresh\_token)

OAuth token endpoint

    Exchange authorization code for access token or refresh an existing token. Supports both authorization code exchange and refresh token flows. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **grant\_type** | **String**|  | [optional] [default to null] [enum: refresh_token] |
| **client\_id** | **String**|  | [optional] [default to null] |
| **client\_secret** | **String**|  | [optional] [default to null] |
| **code** | **String**|  | [optional] [default to null] |
| **redirect\_uri** | **String**|  | [optional] [default to null] |
| **code\_verifier** | **String**| PKCE code verifier | [optional] [default to null] |
| **refresh\_token** | **String**|  | [optional] [default to null] |

### Return type

[**TokenResponse**](../Models/TokenResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/x-www-form-urlencoded
- **Accept**: application/json

