# `dockerd-exporter`

The docker docs show that you can [change the docker daemon settings](https://docs.docker.com/config/daemon/prometheus/)
such that a metrics endpoint is exposed that you can hit locally.

Ordinarily, these settings would be configured using CLI arguments with the `dockerd` command.
However, on a Mac, you don't have direct access to `dockerd`. The only way you can apply `dockerd`
configurations is by editing the `dockerd` JSON file.

Following the directions in the docs, I added some keys to my existing JSON file
using Docker Desktop so that it looks like this:

```json
{
  "features": {
    "buildkit": true
  },
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  // fields added from the docker docs
  "metrics-addr" : "127.0.0.1:9323",
  "experimental" : true
}
```

The GitHub repo that I took the inspiration from to export metrics this way
showed that you can edit the `dockerd` `systemd` configuration (on Linux machines
only) so that `dockerd` starts up with the correct arguments.

| Create or edit `/etc/systemd/system/docker.service.d/docker.conf`, enable the experimental feature and set the metrics address to `0.0.0.0`:

```bash
# /etc/systemd/system/docker.service.d/docker.conf

[Service]
ExecStart=
ExecStart=/usr/bin/dockerd -H fd:// \
  --storage-driver=overlay2 \
  --dns 8.8.4.4 --dns 8.8.8.8 \
  --log-driver json-file \
  --log-opt max-size=50m --log-opt max-file=10 \
  --experimental=true \
  --metrics-addr 0.0.0.0:9323
```

Great, now we need to know the local IP address on the host machine running
`dockerd` where the `dockerd` is listening with the metrics endpoint (you can
probably tell, I'm not even sure what I'm saying here).

Here's an [explanation of the `docker_gwbridge`](https://stackoverflow.com/questions/66445025/meaning-of-abbreviation-docker-gwbridge-or-what-does-gw-actually-mean).

```bash
docker run --rm --net host alpine ip -o addr show docker_gwbridge
```

From the output of this command, grab the docker subnet Gateway IP address. It should
look something like this `172.18.0.1/16`. This is a network interface that exists
in all the docker containers.
