#!/usr/bin/env python3
import docker
import os
import sys

sys.stdout.reconfigure(line_buffering=True)
APP_NET_NAME = os.environ.get("APP_NET_NAME", "app-net")
LOCAL_PORT_ENV = "VIRTUAL_PORT"

client = docker.from_env()

def ensure_network():
    """Ensure the shared application network exists."""
    try:
        net = client.networks.get(APP_NET_NAME)
        print(f"[+] Using existing network: {APP_NET_NAME}")
        return net
    except docker.errors.NotFound:
        print(f"[+] Creating network: {APP_NET_NAME}")
        return client.networks.create(APP_NET_NAME, driver="bridge")

def get_env(container, key):
    """Get environment variable from a container (if set)."""
    env = container.attrs["Config"].get("Env", [])
    for e in env:
        if e.startswith(f"{key}="):
            return e.split("=", 1)[1]
    return None

def handle_container_start(container, app_net):
    """Handle new container startup logic."""
    cname = container.name
    net_mode = container.attrs["HostConfig"]["NetworkMode"]

    local_port = get_env(container, LOCAL_PORT_ENV)
    if not local_port:
        print(f"[-] Container {cname} has no {LOCAL_PORT_ENV}, ignoring")
        return

    if net_mode == "host":
        print(f"[!] Container {cname} runs in host mode. "
              f"Use host.docker.internal:{local_port} to access it.")
    else:
        # Connect container to shared network if not already connected
        networks = container.attrs["NetworkSettings"]["Networks"]
        if APP_NET_NAME not in networks:
            print(f"[+] Connecting {cname} to {APP_NET_NAME}")
            app_net.connect(container)
        else:
            print(f"[=] {cname} already connected to {APP_NET_NAME}")

def watch_events(app_net):
    """Watch Docker events for container lifecycle changes."""
    for event in client.events(decode=True):
        try:
            if event["Type"] == "container" and event["Action"] == "start":
                cid = event["id"]
                container = client.containers.get(cid)
                handle_container_start(container, app_net)
        except Exception as e:
            print(f"[!] Error handling event: {e}")

if __name__ == "__main__":

    net = ensure_network()

    # Scan existing containers at startup
    print("[+] Scanning existing containers...")
    for c in client.containers.list():
        handle_container_start(c, net)

    print("[+] Watching for new containers...")
    watch_events(net)