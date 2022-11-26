import os
import re

OVERRIDE_HOST_ENV_VAR = 'DATABASE_HOST_OVERRIDE'
OVERRIDE_PORT_ENV_VAR = 'DATABASE_PORT_OVERRIDE'

on_swarm = os.getenv('ON_SWARM', '0')
if on_swarm == '1':
    CONN_MAX_AGE = None


def get_docker_host():
    """
    Looks for the DOCKER_HOST environment variable to find the VM
    running docker-machine.

    If the environment variable is not found, it is assumed that
    you're running docker on localhost.
    """
    d_host = os.getenv('DOCKER_HOST', None)
    if d_host:
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', d_host):
            return d_host

        return re.match(r'tcp://(.*?):\d+', d_host).group(1)
    return 'localhost'


def in_docker():
    """Check if we are running in a Docker container.

    The presence of a /.dockerenv file on the root filesystem in Linux is probably a
    more reliable way to know that you’re running inside a Docker container.

    :return: True when running in a Docker container, False otherwise
    """
    if os.path.isfile('/.dockerenv') or os.getenv('OS_ENV') == "container":
        return True
    try:
        with open('/proc/1/sched', 'r') as sched_info:
            if sched_info.readline().startswith('bash '):
                return True
            return False
    except IOError:
        return False
    return False


class LocationKey:
    local = 'local'
    docker = 'docker'
    override = 'override'


def get_database_key():
    if os.getenv(OVERRIDE_HOST_ENV_VAR):
        return LocationKey.override
    if in_docker():
        return LocationKey.docker

    return LocationKey.local
