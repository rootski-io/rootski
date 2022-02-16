When the project was running on a spot instance, traefik handled managing TLS/SSL certs
and proxying various URLs to the right service. Currently we have no servers that
require proxying so this code is inactive.

One change that led to archiving this was moving the Rootski FastAPI app into
AWS lambda. The API Gateway takes care of managing certs for HTTPS for requests
going to the lambda deployment of the API.