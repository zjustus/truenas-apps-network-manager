# TrueNAS Apps Network Manager

TrueNAS has recently switched apps frameworks from k3's to base docker. They are beginning to experiment with LSC, I am against this for my purposes.

I believe when using k3's applications had no trouble talking to each other without ports being exposed on the host IP address. It seams this ability has not quite caught up on TrueNAS docker engine just yet.

This small script aims to fix this problem for the time being by monitoring the docker service and connecting new containers with a specified environment variable into a unified network.

There are a few practical applications of this effort of course, but mine is probably the most basic. SECURE THE APPS WITH TLS CERTIFICATES!! either by reverse proxy like nginx-proxy or something more clever like cloudflare zero trust.

# Running the Manager

**Manager**  
copy this yaml into a custom app in TrueNAS

```yaml
x-network-name: &app_net_name proxy-net
services:
    net-manager:
        build:
            context: https://github.com/zjustus/truenas-apps-network-manager.git
        restart: unless-stopped
		environment:
            APP_NET_NAME: *app_net_name
        volumes:
            - /var/run/docker.sock:/var/run/docker.sock
		networks:
            - proxy-net
networks:
	proxy-net:
		name: *app_net_name
        driver: bridge
```

**Other Apps**  
add the environment variable `VIRTUAL_PORT` to a container and this manager should pick it up.

**HOST APPS**  
if an app requires the docker host network, be sure to add `host.docker.internal` to the reverse proxy container

```yaml
services:
	reverse-proxy:
		extra_hosts:
      		- "host.docker.internal:host-gateway"
```
