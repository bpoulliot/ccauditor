import os
import socket
import time
from urllib.parse import urlparse


def parse_host_port(url):
    parsed = urlparse(url)

    host = parsed.hostname
    port = parsed.port

    if not host or not port:
        raise RuntimeError(f"Invalid connection URL: {url}")

    return host, port


def wait_for_service(host, port, timeout=180):

    start = time.time()
    delay = 0.2  # start fast

    while True:
        try:
            with socket.create_connection((host, port), timeout=2):
                print(f"{host}:{port} is available")
                return
        except OSError:

            elapsed = time.time() - start

            if elapsed > timeout:
                raise RuntimeError(
                    f"Timeout waiting for {host}:{port} after {timeout} seconds"
                )

            time.sleep(delay)

            # exponential backoff up to 2 seconds
            delay = min(delay * 1.5, 2.0)


if __name__ == "__main__":

    database_url = os.getenv("DATABASE_URL")
    redis_url = os.getenv("REDIS_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable not set")

    if not redis_url:
        raise RuntimeError("REDIS_URL environment variable not set")

    db_host, db_port = parse_host_port(database_url)
    redis_host, redis_port = parse_host_port(redis_url)

    print("Checking database availability...")
    wait_for_service(db_host, db_port)

    print("Checking Redis availability...")
    wait_for_service(redis_host, redis_port)

    print("All dependencies are ready.")