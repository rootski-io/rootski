# The Rootski VPN

A VPN gives us two things:

1. a way to network both the on-premise machine and VMs in AWS (makes docker swarm easy)
2. a way rootski admins can access monitoring, jupyter notebooks, the database, etc. on the on-prem machine
without exposing those sensitive services to the world
3. an added layer of security in our hybrid on-prem and cloud architecture: all rootski traffic
passed from the EC2 instance to the on-prem machine will be encrypted

## Research on running Wireguard docker

> The following paragraphs are notes that I took for myself while trying to
get the wireguard setup in the `docker-compose.yml` working on an AWS Lightsail instance:

After running this file and connecting the client,
`ping 10.13.13.1` from the client should work to ping the VPN server.
However, running `python -m http.server` on the server DOES NOT cause
`telnet 10.13.13.1 8000` to work on the client. BUT if we run a hello-world
flask app in docker on port 5000 AND configure that container to send its
traffic through the wireguard container like so:

`docker run --net container:<wireguard container id> digitalocean/flask-helloworld`
then `telnet 10.13.13.1 5000` on the client DOES work. This leads me to believe that,
by default, applications on the VPN server do not automatically send and/or receive
traffic through the VPN interface... because there is no VPN interface on the VPN server.
The VPN interface (wg0) would be configured inside the docker container.

Another clue! On the VPN server, if I run `docker exec -it <wireguard container> /bin/bash`
and then run `apt-get update; apt-get install python3.6; python3.6 -m http.server` and THEN
on the client if I run `telnet 10.13.13.1 8000` IT WORKS. Conclusion: the 10.13.13.1
IP address is actually only valid inside the docker container on the VPN server. When the client
runs `telnet 10.13.13.1 8000` AFTER connecting via the Wireguard client app, the Wireguard
client app catches my outgoing traffic on port 8000, it encrypts it, and then it sends it
to the EC2 public IP address on port 51820 since that`s the port the Wireguard container
is listening on / has published.

This... won`t work for docker swarm. I need docker swarm to run on the host machine of the VPN
server. Could the EC2 instance host be a peer of wireguard server running in the Docker container?
That would actually be circular. We`d need to enable docker swarm mode BEFORE starting the wireguard
container so that we could run the wireguard container as a swarm container for automatic restarts.
But to enable swarm mode, you have to set the `--listen-addr` field... which requires a private IP
issued by the wireguard server (or the wg0 interface). No, it`s probably best to run wireguard
completely outside of docker so that no wireguard-specific configuration ends up in the rootski
docker-compose files.
