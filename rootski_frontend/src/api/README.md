Hello!

Quick note on axios: axios is essentially a global variable.
In the `redux/actions/AuthActions.tsx:loginUserAction` actually
sets the default authorization header for ALL requests that axios
makes later.

Yes, this token can be overriden in the functions here in the `api` folder.
But in practice, they don't need to be.

In parts of the codebase, we have components manually grabbing the auth token
off of the state and passing it to the token. If I'd known about the global
variable thing earlier, I would not have done it that way (probably).

This DID fix an issue where users weren't seeing their submitted breakdowns
because axios wasn't getting the token in the request for some reason.
