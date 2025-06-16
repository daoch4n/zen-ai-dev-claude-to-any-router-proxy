# CertificatesApi

All URIs are relative to *https://api.openai.com/v1*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**activateOrganizationCertificates**](CertificatesApi.md#activateOrganizationCertificates) | **POST** /organization/certificates/activate | Activate certificates at the organization level.  You can atomically and idempotently activate up to 10 certificates at a time.  |
| [**activateProjectCertificates**](CertificatesApi.md#activateProjectCertificates) | **POST** /organization/projects/{project_id}/certificates/activate | Activate certificates at the project level.  You can atomically and idempotently activate up to 10 certificates at a time.  |
| [**deactivateOrganizationCertificates**](CertificatesApi.md#deactivateOrganizationCertificates) | **POST** /organization/certificates/deactivate | Deactivate certificates at the organization level.  You can atomically and idempotently deactivate up to 10 certificates at a time.  |
| [**deactivateProjectCertificates**](CertificatesApi.md#deactivateProjectCertificates) | **POST** /organization/projects/{project_id}/certificates/deactivate | Deactivate certificates at the project level.  You can atomically and idempotently deactivate up to 10 certificates at a time.  |
| [**deleteCertificate**](CertificatesApi.md#deleteCertificate) | **DELETE** /organization/certificates/{certificate_id} | Delete a certificate from the organization.  The certificate must be inactive for the organization and all projects.  |
| [**getCertificate**](CertificatesApi.md#getCertificate) | **GET** /organization/certificates/{certificate_id} | Get a certificate that has been uploaded to the organization.  You can get a certificate regardless of whether it is active or not.  |
| [**listOrganizationCertificates**](CertificatesApi.md#listOrganizationCertificates) | **GET** /organization/certificates | List uploaded certificates for this organization. |
| [**listProjectCertificates**](CertificatesApi.md#listProjectCertificates) | **GET** /organization/projects/{project_id}/certificates | List certificates for this project. |
| [**modifyCertificate**](CertificatesApi.md#modifyCertificate) | **POST** /organization/certificates/{certificate_id} | Modify a certificate. Note that only the name can be modified.  |
| [**uploadCertificate**](CertificatesApi.md#uploadCertificate) | **POST** /organization/certificates | Upload a certificate to the organization. This does **not** automatically activate the certificate.  Organizations can upload up to 50 certificates.  |


<a name="activateOrganizationCertificates"></a>
# **activateOrganizationCertificates**
> ListCertificatesResponse activateOrganizationCertificates(ToggleCertificatesRequest)

Activate certificates at the organization level.  You can atomically and idempotently activate up to 10 certificates at a time. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **ToggleCertificatesRequest** | [**ToggleCertificatesRequest**](../Models/ToggleCertificatesRequest.md)| The certificate activation payload. | |

### Return type

[**ListCertificatesResponse**](../Models/ListCertificatesResponse.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="activateProjectCertificates"></a>
# **activateProjectCertificates**
> ListCertificatesResponse activateProjectCertificates(ToggleCertificatesRequest)

Activate certificates at the project level.  You can atomically and idempotently activate up to 10 certificates at a time. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **ToggleCertificatesRequest** | [**ToggleCertificatesRequest**](../Models/ToggleCertificatesRequest.md)| The certificate activation payload. | |

### Return type

[**ListCertificatesResponse**](../Models/ListCertificatesResponse.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="deactivateOrganizationCertificates"></a>
# **deactivateOrganizationCertificates**
> ListCertificatesResponse deactivateOrganizationCertificates(ToggleCertificatesRequest)

Deactivate certificates at the organization level.  You can atomically and idempotently deactivate up to 10 certificates at a time. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **ToggleCertificatesRequest** | [**ToggleCertificatesRequest**](../Models/ToggleCertificatesRequest.md)| The certificate deactivation payload. | |

### Return type

[**ListCertificatesResponse**](../Models/ListCertificatesResponse.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="deactivateProjectCertificates"></a>
# **deactivateProjectCertificates**
> ListCertificatesResponse deactivateProjectCertificates(ToggleCertificatesRequest)

Deactivate certificates at the project level.  You can atomically and idempotently deactivate up to 10 certificates at a time. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **ToggleCertificatesRequest** | [**ToggleCertificatesRequest**](../Models/ToggleCertificatesRequest.md)| The certificate deactivation payload. | |

### Return type

[**ListCertificatesResponse**](../Models/ListCertificatesResponse.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="deleteCertificate"></a>
# **deleteCertificate**
> DeleteCertificateResponse deleteCertificate()

Delete a certificate from the organization.  The certificate must be inactive for the organization and all projects. 

### Parameters
This endpoint does not need any parameter.

### Return type

[**DeleteCertificateResponse**](../Models/DeleteCertificateResponse.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getCertificate"></a>
# **getCertificate**
> Certificate getCertificate(cert\_id, include)

Get a certificate that has been uploaded to the organization.  You can get a certificate regardless of whether it is active or not. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **cert\_id** | **String**| Unique ID of the certificate to retrieve. | [default to null] |
| **include** | [**List**](../Models/String.md)| A list of additional fields to include in the response. Currently the only supported value is &#x60;content&#x60; to fetch the PEM content of the certificate. | [optional] [default to null] [enum: content] |

### Return type

[**Certificate**](../Models/Certificate.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="listOrganizationCertificates"></a>
# **listOrganizationCertificates**
> ListCertificatesResponse listOrganizationCertificates(limit, after, order)

List uploaded certificates for this organization.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **limit** | **Integer**| A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.  | [optional] [default to 20] |
| **after** | **String**| A cursor for use in pagination. &#x60;after&#x60; is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include after&#x3D;obj_foo in order to fetch the next page of the list.  | [optional] [default to null] |
| **order** | **String**| Sort order by the &#x60;created_at&#x60; timestamp of the objects. &#x60;asc&#x60; for ascending order and &#x60;desc&#x60; for descending order.  | [optional] [default to desc] [enum: asc, desc] |

### Return type

[**ListCertificatesResponse**](../Models/ListCertificatesResponse.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="listProjectCertificates"></a>
# **listProjectCertificates**
> ListCertificatesResponse listProjectCertificates(limit, after, order)

List certificates for this project.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **limit** | **Integer**| A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.  | [optional] [default to 20] |
| **after** | **String**| A cursor for use in pagination. &#x60;after&#x60; is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include after&#x3D;obj_foo in order to fetch the next page of the list.  | [optional] [default to null] |
| **order** | **String**| Sort order by the &#x60;created_at&#x60; timestamp of the objects. &#x60;asc&#x60; for ascending order and &#x60;desc&#x60; for descending order.  | [optional] [default to desc] [enum: asc, desc] |

### Return type

[**ListCertificatesResponse**](../Models/ListCertificatesResponse.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="modifyCertificate"></a>
# **modifyCertificate**
> Certificate modifyCertificate(ModifyCertificateRequest)

Modify a certificate. Note that only the name can be modified. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **ModifyCertificateRequest** | [**ModifyCertificateRequest**](../Models/ModifyCertificateRequest.md)| The certificate modification payload. | |

### Return type

[**Certificate**](../Models/Certificate.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="uploadCertificate"></a>
# **uploadCertificate**
> Certificate uploadCertificate(UploadCertificateRequest)

Upload a certificate to the organization. This does **not** automatically activate the certificate.  Organizations can upload up to 50 certificates. 

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **UploadCertificateRequest** | [**UploadCertificateRequest**](../Models/UploadCertificateRequest.md)| The certificate upload payload. | |

### Return type

[**Certificate**](../Models/Certificate.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

