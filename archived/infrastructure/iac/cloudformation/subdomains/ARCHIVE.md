These scripts and this CF template were used when Rootski was deployed on a spot instance.
The `apply.xsh` script pointed several subdomains at the IP address on the spot instance.

Now that (a) the FastAPI app is deployed in lambda, and (b) the database runs on a
lightsail instance which is routed to with a Fully Qualified Domain Name (FQDN),
it is no longer necessary to configure subdomains to point at a new IP address on startup.
