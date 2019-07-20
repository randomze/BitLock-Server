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
HTTP/1.1 200

{
    "message": "value updated successfully"
}
```

*Failure*

```json
HTTP/1.1 4xx

{
    "message": "failed to update resource",
    "error": "somecode"
}
```

Provisional structure

/register_user[/] - returns the user identifier for some user that just registered himself.
    TODO: - Check for repeated calls and block. (One user register per IP per hour?)

/user/<string:UUID> - root structure for a user. Unsure of whether or not this is an acessible URL

/user/<string:UUID>/devices/ - root structure for the devices a user owns. Unsure if this is an acessible URL and it returns all the devices or whether devices/all should serve that purpose.

/user/<string:UUID>/devices/<string:device_identifier> - returns the current status of the device queried

TODO: revise the communication mechanisms through which the devices are notified to change their status and through which these communicate alterations in their status. Webhooks?