# Traefik v2.x

## Traefik Object Model

When you send a request to traefik, the request goes through the following flow:
             entrypoint -> router -> middleware(s) -> service

### Entrypoint

there is a "web" entrypoint when the request path starts with "http". "websecure" is for "https".

*Note* these are actually defined in the static config and referenced from the dynamic config.
I've renamed "web" to "http", and "websecure" to "https". Entrypoints are basically an alias to
a range of ports and maybe IP address ranges.

### Router

after determining the entrypoint of the request path, traefik checks for routers that match the request path
the job of a router is to tell traefik which docker service to send the request to. But before it does that,
it can process the request a bit by sending it through one or more "middlewares". Middlewares are pre-defined
in the traefik code.

### Middleware

A router can route a request through any number of middlewares
before sending the request to its final destination. There are some cool ones like

#### "basicAuth"

makes the request have to have a "username:password" in the "Authorization" header
or else traefik will just return a 401 response

#### "redirectScheme"

a "scheme" is the first part of a request, e.g. http:// or https://. You can
force requests starting with http:// to go through the https:// router.
Therefore, the only requests allowed to go through traffic are https requests.

#### "rateLimit"

If a certain IP address is sending too many requests, you can DENY THEM! Awesome.
There are a bunch more middlewares on the docs page. It's easiest to understand the YAML configuration
for them.

### service

A "service" is literally s service. Like a service running in docker.
It could be the frontend, backend, database, or anything
else under the "services:" section of a docker-compose.yml. You DO have to explicitly create
a "service" in the traefik config that explicitly maps to a service in the "services:" section.

## Traefik Configuration

There are two types of configuration in Traefik: *dynamic configuration* and *static configuration*.

### Dynamic Config

Each of the four items listed above are objects in Traefik.
They are pieces of config that you have to define in the *dynamic configuration*.

### Static Config

The *static* configuration is for... everything that isn't these four things. So,
setting up the ACME TLS cert resolver with LetsEncrypt, telling traefik where to
look to find the dynamic config, what port traefik should run on. Basically,
static config is anything Traefik needs to know when it starts up.

But wait! Where do you normally put config for a service at startup time?
In the CLI arguments! (or environment variables, but I don't think Traefik supports that).
So, you have two options for static config. You can stick it in the CLI variables, or
you can stick it in a file (TOML or YAML). To make Traefik actually use the file,
you DO have to pass in a CLI argument (`--configFile=`).

### Back to Dynamic Config

Dynamic config can come from multiple sources. These sources are called "providers".
You could create dynamic config objects in the labels of the `docker-compose.yml` file
(ONLY when you run it with docker swarm, though). This is called the `docker` provider.
Again, docker *swarm* is the `docker` provider. Here's an example:

```yaml
services:
    some-api:
        deploy:
            labels:
                - some dynamic config for traefik
                - some more dynamic config for traefik
```

You can use the `docker` provider and/or the `file` provider. The static config
can register a bunch of providers including kubernetes (which also uses labels incidentally).
So yes, you would create a YAML file called something like `dynamic-config.yml` and include
`path/to/dynamic-config.yml` somewhere in the `static-config.yml` to set that up.

You can reference dynamic config objects created by the file provider in the docker swarm labels
and vice versa. To reference an object defined by the file provider, you use `<object name>@file`.
To reference an object defined by the `docker` (docker swarm) provider, you use
`<object name>@docker`. So basically, you can reference objects with `<object name>@<provider name>`
as long as the provider you're using is registered in the static config.

## Notes on debugging

Due to the way we've configured traefik, running `docker logs -f <traefik container id>`
doesn't give you much. Instead, see the `traefik.log` file. `cat traefik.log | less`.

# LetsEncrypt and HTTPS


This is a fantastic video about TXT DNS records. We're using Route53 for our DNS.
https://www.youtube.com/watch?v=x28TGYX9NW4&ab_channel=TonyTeachesTech

This is a fantastic video about the DNS-01 challenge with traefik and Route53 in AWS
(all the videos in this series are really helpful). The only issue is that it uses
Traefik v1. The concepts he shows are really helpful, though:
https://www.youtube.com/watch?v=wTHg7M9LY34&ab_channel=EficodePraqma

Render the PlantUML diagrams in this file to see more visual aids on how Traefik
gets its certificates using letsencrypt.
