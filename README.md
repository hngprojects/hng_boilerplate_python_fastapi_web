---
title: HNG Boilerplate API v1.0.0
language_tabs:
  - shell: Shell
  - python: Python
language_clients:
  - shell: ""
  - python: ""
toc_footers: []
includes: []
search: false
highlight_theme: darkula
headingLevel: 2
---

<!-- Generator: Widdershins v4.0.1 -->

<h1 id="hng-boilerplate-api">HNG Boilerplate API v1.0.0</h1>

> Scroll down for code samples, example requests and responses. Select a language for code samples from the tabs above or the mobile navigation menu.

API Boilerplate for HNG Task

Base URLs:

- <a href="http://127.0.0.1">http://127.0.0.1</a>

# Authentication

- HTTP Authentication, scheme: bearer

<h1 id="hng-boilerplate-api-default">Default</h1>

## Gets all payments made by user

> Code samples

```shell
# You can also use wget
curl -X GET http://127.0.0.1/api/payments \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer {access-token}'

```

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.get('http://127.0.0.1/api/payments', headers = headers)

print(r.json())

```

`GET /api/payments`

> Example responses

> 200 Response

```json
[
  {
    "id": "string",
    "amount": 0,
    "currency": "string",
    "status": "string",
    "createdAt": "string"
  }
]
```

<h3 id="gets-all-payments-made-by-user-responses">Responses</h3>

| Status | Meaning                                                         | Description                     | Schema                      |
| ------ | --------------------------------------------------------------- | ------------------------------- | --------------------------- |
| 200    | [OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)         | All payments were returned      | Inline                      |
| 401    | [Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1) | Request requires authentication | [Error401](#schemaerror401) |

<h3 id="gets-all-payments-made-by-user-responseschema">Response Schema</h3>

Status Code **200**

| Name        | Type                          | Required | Restrictions | Description                        |
| ----------- | ----------------------------- | -------- | ------------ | ---------------------------------- |
| _anonymous_ | [[Payment](#schemapayment)]   | false    | none         | none                               |
| » id        | [PaymentId](#schemapaymentid) | true     | none         | The unique identifier of a payment |
| » amount    | integer                       | true     | none         | none                               |
| » currency  | string                        | true     | none         | none                               |
| » status    | string                        | true     | none         | none                               |
| » createdAt | string                        | true     | none         | none                               |

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
bearerAuth
</aside>

## Creates a payment record

> Code samples

```shell
# You can also use wget
curl -X POST http://127.0.0.1/api/payments \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer {access-token}'

```

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.post('http://127.0.0.1/api/payments', headers = headers)

print(r.json())

```

`POST /api/payments`

> Body parameter

```json
{
  "amount": 0,
  "currency": "string",
  "status": "string",
  "createdAt": "string"
}
```

<h3 id="creates-a-payment-record-parameters">Parameters</h3>

| Name | In   | Type                              | Required | Description |
| ---- | ---- | --------------------------------- | -------- | ----------- |
| body | body | [PaymentPost](#schemapaymentpost) | true     | none        |

> Example responses

> 201 Response

```json
{
  "id": "string",
  "amount": 0,
  "currency": "string",
  "status": "string",
  "createdAt": "string"
}
```

<h3 id="creates-a-payment-record-responses">Responses</h3>

| Status | Meaning                                                          | Description                         | Schema                      |
| ------ | ---------------------------------------------------------------- | ----------------------------------- | --------------------------- |
| 201    | [Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)     | Payment record created successfully | [Payment](#schemapayment)   |
| 400    | [Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1) | Request malformed                   | [Error400](#schemaerror400) |
| 401    | [Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)  | Request requires authentication     | [Error401](#schemaerror401) |

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
bearerAuth
</aside>

## Gets a Single Payment

> Code samples

```shell
# You can also use wget
curl -X GET http://127.0.0.1/api/payments/{payment_id} \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer {access-token}'

```

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.get('http://127.0.0.1/api/payments/{payment_id}', headers = headers)

print(r.json())

```

`GET /api/payments/{payment_id}`

<h3 id="gets-a-single-payment-parameters">Parameters</h3>

| Name       | In   | Type                          | Required | Description                               |
| ---------- | ---- | ----------------------------- | -------- | ----------------------------------------- |
| payment_id | path | [PaymentId](#schemapaymentid) | true     | The unique identifier of a payment record |

> Example responses

> 200 Response

```json
{
  "id": "string",
  "amount": 0,
  "currency": "string",
  "status": "string",
  "createdAt": "string"
}
```

<h3 id="gets-a-single-payment-responses">Responses</h3>

| Status | Meaning                                                         | Description                        | Schema                      |
| ------ | --------------------------------------------------------------- | ---------------------------------- | --------------------------- |
| 200    | [OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)         | Single payment object was returned | [Payment](#schemapayment)   |
| 401    | [Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1) | Request requires authentication    | [Error401](#schemaerror401) |
| 404    | [Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)  | Required resource not found        | [Error404](#schemaerror404) |

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
bearerAuth
</aside>

## Delete a payment record

> Code samples

```shell
# You can also use wget
curl -X DELETE http://127.0.0.1/api/payments/{payment_id} \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer {access-token}'

```

```python
import requests
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.delete('http://127.0.0.1/api/payments/{payment_id}', headers = headers)

print(r.json())

```

`DELETE /api/payments/{payment_id}`

<h3 id="delete-a-payment-record-parameters">Parameters</h3>

| Name       | In   | Type                          | Required | Description                               |
| ---------- | ---- | ----------------------------- | -------- | ----------------------------------------- |
| payment_id | path | [PaymentId](#schemapaymentid) | true     | The unique identifier of a payment record |

> Example responses

> 401 Response

```json
{
  "message": "string",
  "code": 0
}
```

<h3 id="delete-a-payment-record-responses">Responses</h3>

| Status | Meaning                                                         | Description                         | Schema                      |
| ------ | --------------------------------------------------------------- | ----------------------------------- | --------------------------- |
| 204    | [No Content](https://tools.ietf.org/html/rfc7231#section-6.3.5) | Payment record deleted successfully | None                        |
| 401    | [Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1) | Request requires authentication     | [Error401](#schemaerror401) |
| 404    | [Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)  | Required resource not found         | [Error404](#schemaerror404) |

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
bearerAuth
</aside>

## Gets all payment providers available

> Code samples

```shell
# You can also use wget
curl -X GET http://127.0.0.1/api/payments-providers \
  -H 'Accept: application/json'

```

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('http://127.0.0.1/api/payments-providers', headers = headers)

print(r.json())

```

`GET /api/payments-providers`

> Example responses

> 200 Response

```json
[
  {
    "provider_id": "string",
    "provider_name": "string"
  }
]
```

<h3 id="gets-all-payment-providers-available-responses">Responses</h3>

| Status | Meaning                                                 | Description                 | Schema |
| ------ | ------------------------------------------------------- | --------------------------- | ------ |
| 200    | [OK](https://tools.ietf.org/html/rfc7231#section-6.3.1) | All providers were returned | Inline |

<h3 id="gets-all-payment-providers-available-responseschema">Response Schema</h3>

Status Code **200**

| Name            | Type                          | Required | Restrictions | Description |
| --------------- | ----------------------------- | -------- | ------------ | ----------- |
| _anonymous_     | [[Provider](#schemaprovider)] | false    | none         | none        |
| » provider_id   | string                        | true     | none         | none        |
| » provider_name | string                        | true     | none         | none        |

<aside class="success">
This operation does not require authentication
</aside>

## Gets a single payment provider

> Code samples

```shell
# You can also use wget
curl -X GET http://127.0.0.1/api/payments-providers/{provider_id} \
  -H 'Accept: application/json'

```

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('http://127.0.0.1/api/payments-providers/{provider_id}', headers = headers)

print(r.json())

```

`GET /api/payments-providers/{provider_id}`

<h3 id="gets-a-single-payment-provider-parameters">Parameters</h3>

| Name        | In   | Type   | Required | Description                                 |
| ----------- | ---- | ------ | -------- | ------------------------------------------- |
| provider_id | path | string | true     | The unique identifier of a payment provider |

> Example responses

> 200 Response

```json
{
  "provider_id": "string",
  "provider_name": "string"
}
```

<h3 id="gets-a-single-payment-provider-responses">Responses</h3>

| Status | Meaning                                                        | Description                         | Schema                      |
| ------ | -------------------------------------------------------------- | ----------------------------------- | --------------------------- |
| 200    | [OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)        | Single provider object was returned | [Provider](#schemaprovider) |
| 404    | [Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4) | Required resource not found         | [Error404](#schemaerror404) |

<aside class="success">
This operation does not require authentication
</aside>

# Schemas

<h2 id="tocS_PaymentId">PaymentId</h2>
<!-- backwards compatibility -->
<a id="schemapaymentid"></a>
<a id="schema_PaymentId"></a>
<a id="tocSpaymentid"></a>
<a id="tocspaymentid"></a>

```json
"string"
```

The unique identifier of a payment

### Properties

| Name        | Type   | Required | Restrictions | Description                        |
| ----------- | ------ | -------- | ------------ | ---------------------------------- |
| _anonymous_ | string | false    | none         | The unique identifier of a payment |

<h2 id="tocS_Payment">Payment</h2>
<!-- backwards compatibility -->
<a id="schemapayment"></a>
<a id="schema_Payment"></a>
<a id="tocSpayment"></a>
<a id="tocspayment"></a>

```json
{
  "id": "string",
  "amount": 0,
  "currency": "string",
  "status": "string",
  "createdAt": "string"
}
```

### Properties

| Name      | Type                          | Required | Restrictions | Description                        |
| --------- | ----------------------------- | -------- | ------------ | ---------------------------------- |
| id        | [PaymentId](#schemapaymentid) | true     | none         | The unique identifier of a payment |
| amount    | integer                       | true     | none         | none                               |
| currency  | string                        | true     | none         | none                               |
| status    | string                        | true     | none         | none                               |
| createdAt | string                        | true     | none         | none                               |

<h2 id="tocS_PaymentPost">PaymentPost</h2>
<!-- backwards compatibility -->
<a id="schemapaymentpost"></a>
<a id="schema_PaymentPost"></a>
<a id="tocSpaymentpost"></a>
<a id="tocspaymentpost"></a>

```json
{
  "amount": 0,
  "currency": "string",
  "status": "string",
  "createdAt": "string"
}
```

### Properties

| Name      | Type    | Required | Restrictions | Description |
| --------- | ------- | -------- | ------------ | ----------- |
| amount    | integer | true     | none         | none        |
| currency  | string  | true     | none         | none        |
| status    | string  | true     | none         | none        |
| createdAt | string  | false    | none         | none        |

<h2 id="tocS_Provider">Provider</h2>
<!-- backwards compatibility -->
<a id="schemaprovider"></a>
<a id="schema_Provider"></a>
<a id="tocSprovider"></a>
<a id="tocsprovider"></a>

```json
{
  "provider_id": "string",
  "provider_name": "string"
}
```

### Properties

| Name          | Type   | Required | Restrictions | Description |
| ------------- | ------ | -------- | ------------ | ----------- |
| provider_id   | string | true     | none         | none        |
| provider_name | string | true     | none         | none        |

<h2 id="tocS_Error404">Error404</h2>
<!-- backwards compatibility -->
<a id="schemaerror404"></a>
<a id="schema_Error404"></a>
<a id="tocSerror404"></a>
<a id="tocserror404"></a>

```json
{
  "message": "string",
  "code": 0
}
```

### Properties

| Name    | Type    | Required | Restrictions | Description |
| ------- | ------- | -------- | ------------ | ----------- |
| message | string  | false    | none         | Not found   |
| code    | integer | false    | none         | none        |

<h2 id="tocS_Error401">Error401</h2>
<!-- backwards compatibility -->
<a id="schemaerror401"></a>
<a id="schema_Error401"></a>
<a id="tocSerror401"></a>
<a id="tocserror401"></a>

```json
{
  "message": "string",
  "code": 0
}
```

### Properties

| Name    | Type    | Required | Restrictions | Description            |
| ------- | ------- | -------- | ------------ | ---------------------- |
| message | string  | false    | none         | Authentication failure |
| code    | integer | false    | none         | none                   |

<h2 id="tocS_Error400">Error400</h2>
<!-- backwards compatibility -->
<a id="schemaerror400"></a>
<a id="schema_Error400"></a>
<a id="tocSerror400"></a>
<a id="tocserror400"></a>

```json
{
  "message": "string",
  "code": 0
}
```

### Properties

| Name    | Type    | Required | Restrictions | Description       |
| ------- | ------- | -------- | ------------ | ----------------- |
| message | string  | false    | none         | Malformed request |
| code    | integer | false    | none         | none              |

## Database Design

![Database Design](./hng_database_design.png)

## Database Documentation

For more detailed information on the database schema and relationships, please refer to the [Database Documentation](https://dbdocs.io/Trevor%20job/hng_database_docs).
