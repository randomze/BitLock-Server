# User and lock register service

## Register a user

**Definition**

`POST /register_user[/]`

**Required Headers**

`Authorization: Basic <base64 encoded passowrd>`

**Response**

*Success*


```json
HTTP/1.1 201 Created
Content-Type: application/json

{
    message: "user created successfully",
    uuid: "some uuid"
}
```

*Failure*

```json
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
    message: "something went wrong while creating the user related to the request",
    error: "some-code perhaps"
}
```
## Get devices under a users control

There exists an endpoint for the devices resources, all, which is to be used when the client wants to know all the devices registered under a user. As such, no device can have «all» as it's identifier.

**Definition**

`GET /user/<UUID:string>/devices/all`

**Required Headers**

`Authorization: Basic <base64 encoded password>`

**Response**

*Success*

```json
HTTP/1.1 200 OK
Content-Type: application/json

{
    "message": "devices for user <UUID:string> fetched",
    "devices_count": "some_number",
    "devices": [
        {
            "device_name": "name",
            "status": "open/closed",
            "permissions": "regular/admin"
        }
    ]
}
```

*Failure*

```json
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
    "message": "bad identification. user or password not existent/matching",
    "error": "some-code perhaps"
}
```

## Update device status

**Definition**

`PUT /user/<UUID:string>/devices/<device_id:string>/<parameter:string>/<value:string>`

**Required Headers**

`Authorization: Basic <base64 encoded password>`

**Response**

*Success*

```json
HTTP/1.1
```



