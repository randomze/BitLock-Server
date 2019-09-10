#User service

To use the user service, the `Authorization` header is always required and it should be set as follows:

`Authorization: `

The response comes in json, with the `Content-Type` header properly set.

##Registering a user

`POST /user/register_user[/]`

The response fields available are:

`message` - contains a summary of the result of the operation
`uuid_string` - the user identifier, which is to be used from here on out. Only returned on **success**
`error_code` - the error code which specifies why the operation failed. Only returned on **failure**

##Deleting a user

`DELETE /user/<string:UUID>`

The response fields available are:

`message` - contains a summary of the result of the operation
`error_code` - the error code which specifies why the operation failed. Only returned on **failure**

##Non-specified URL's

In case you were to try acessing a URL which is not one of the above, a 404 will be returned, with no content. Similarly, if you try to access one of the above URL's with methods which are not the ones described, a 403 will be returned, with no content.

##Error codes

The error codes for the user service are:

`001` - Wrong password
`002` - Unexistent user
`003` - String is not a UUID
`004` - No `Authorization` header
`005` - Authorization is not `Basic`

#Comments and guidelines

Provisional structure

/register_user[/] - returns the user identifier for some user that just registered himself.
    TODO: - Check for repeated calls and block. (One user register per IP per hour?)

/user/<string:UUID> - root structure for a user. Unsure of whether or not this is an acessible URL

/user/<string:UUID>/devices/ - root structure for the devices a user owns. Unsure if this is an acessible URL and it returns all the devices or whether devices/all should serve that purpose.

/user/<string:UUID>/devices/<string:device_identifier> - returns the current status of the device queried

TODO: revise the communication mechanisms through which the devices are notified to change their status and through which these communicate alterations in their status. Webhooks?