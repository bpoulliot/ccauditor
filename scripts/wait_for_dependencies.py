import time
import socket
import os

POSTGRES_HOST = "postgres"
POSTGRES_PORT = 5432

REDIS_HOST = "redis"
REDIS_PORT = 6379


def wait_for_service(host, port):

    while True:
        try:
            sock = socket.create_connection((host, port), timeout=5)
            sock.close()
            return
        except OSError:
            print(f"Waiting for {host}:{port}")
            time.sleep(3)


if __name__ == "__main__":

    print("Checking service readiness...")

    wait_for_service(POSTGRES_HOST, POSTGRES_PORT)
    wait_for_service(REDIS_HOST, REDIS_PORT)

    print("Dependencies ready.")