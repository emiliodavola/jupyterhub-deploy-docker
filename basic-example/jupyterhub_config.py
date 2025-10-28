# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# Configuration file for JupyterHub
import os

c = get_config()  # noqa: F821

# We rely on environment variables to configure JupyterHub so that we
# avoid having to rebuild the JupyterHub container every time we change a
# configuration parameter.

# Spawn single-user servers as Docker containers
c.JupyterHub.spawner_class = "dockerspawner.DockerSpawner"

# Spawn containers from this image
c.DockerSpawner.image = os.environ["DOCKER_NOTEBOOK_IMAGE"]

# Connect containers to this Docker network
network_name = os.environ["DOCKER_NETWORK_NAME"]
c.DockerSpawner.use_internal_ip = True
c.DockerSpawner.network_name = network_name

# Explicitly set notebook directory because we'll be mounting a volume to it.
# Most `jupyter/docker-stacks` *-notebook images run the Notebook server as
# user `jovyan`, and set the notebook directory to `/home/jovyan/work`.
# We follow the same convention.
notebook_dir = os.environ.get("DOCKER_NOTEBOOK_DIR", "/home/jovyan/work")
c.DockerSpawner.notebook_dir = notebook_dir

# Mount the real user's Docker volume on the host to the notebook user's
# notebook directory in the container
c.DockerSpawner.volumes = {"jupyterhub-user-{username}": notebook_dir}

# Keep containers after they stop (temporarily for debugging)
# This lets us inspect logs if the server crashes during start
c.DockerSpawner.remove = True

# For debugging arguments passed to spawned containers
c.DockerSpawner.debug = True

# A mapping of friendly names to Docker images that users are allowed to spawn.
# The keys are the human-readable names shown in the spawn form, and the
# values are the actual image names that DockerSpawner will pull and run.
c.DockerSpawner.allowed_images = {
    "Jupyter base": "jupyter/base-notebook:latest",
    "Jupyter PySpark": "jupyter/pyspark-notebook:latest",
    "Jupyter DS": "jupyter/datascience-notebook:latest",
}

# HTML form presented to users on the spawn page. The <select> values must match
# the keys of `c.DockerSpawner.allowed_images` so that the spawner can map the
# user's selection to an allowed image.
c.DockerSpawner.options_form = """
<label for="image">Select Docker image to spawn:</label>
<select name="image" required>
    <option value="Jupyter base">Jupyter base</option>
    <option value="Jupyter PySpark">Jupyter PySpark</option>
    <option value="Jupyter DS">Jupyter DS</option>
</select>
"""


def options_from_form(formdata):
    # Translate the submitted form value into the dict expected by DockerSpawner.
    # The form submits the friendly key (e.g. "Jupyter base"); return it as the
    # `image` user option so DockerSpawner can look up the actual image.
    selected_key = formdata.get("image", ["Jupyter base"])[0]
    return {"image": selected_key}


c.DockerSpawner.options_from_form = options_from_form

# Increase the time allowed for a single-user server to start
# First-time image pulls can take a while; allow override via env var
start_timeout = int(os.environ.get("SPAWNER_START_TIMEOUT", "600"))
c.Spawner.start_timeout = start_timeout

# Allow more time for the Hub to connect to the single-user server
# after it reports ready (default is ~30s)
http_timeout = int(os.environ.get("SPAWNER_HTTP_TIMEOUT", "300"))
c.Spawner.http_timeout = http_timeout

# User containers will access hub by container name on the Docker network
c.JupyterHub.hub_ip = "jupyterhub"
c.JupyterHub.hub_port = 8080

# Persist hub data on volume mounted inside container
c.JupyterHub.cookie_secret_file = "/data/jupyterhub_cookie_secret"
c.JupyterHub.db_url = "sqlite:////data/jupyterhub.sqlite"

# Allow all signed-up users to login
c.Authenticator.allow_all = True

# Authenticate users with Native Authenticator
c.JupyterHub.authenticator_class = "nativeauthenticator.NativeAuthenticator"

# Allow anyone to sign-up without approval
c.NativeAuthenticator.open_signup = True

# Allowed admins
admin = os.environ.get("JUPYTERHUB_ADMIN")
if admin:
    c.Authenticator.admin_users = [admin]
