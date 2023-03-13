from phidata.app.server import AppServer
from phidata.docker.config import DockerConfig, DockerImage

from workspace.dev.jupyter.docker_resources import dev_jupyter_lab
from workspace.settings import ws_settings

#
# -*- Dev Docker resources
#

# -*- ML Server Image
dev_ml_server_image = DockerImage(
    name=f"{ws_settings.image_repo}/{ws_settings.ws_name}",
    tag=ws_settings.dev_env,
    enabled=(ws_settings.build_images and ws_settings.dev_ml_server_enabled),
    path=str(ws_settings.ws_dir.parent),
    # platform="linux/amd64",
    pull=ws_settings.force_pull_images,
    push_image=ws_settings.push_images,
    skip_docker_cache=ws_settings.skip_image_cache,
    use_cache=ws_settings.use_cache,
)

# -*- App Server running Streamlit on port 9095
dev_app_server = AppServer(
    name=f"{ws_settings.ws_name}-app",
    enabled=ws_settings.dev_ml_server_enabled,
    image=dev_ml_server_image,
    mount_workspace=True,
    use_cache=ws_settings.use_cache,
    secrets_file=ws_settings.ws_dir.joinpath("secrets/app_secrets.yml"),
)

#
# -*- Define dev Docker resources using the DockerConfig
#
dev_docker_config = DockerConfig(
    env=ws_settings.dev_env,
    network=ws_settings.ws_name,
    apps=[dev_app_server, dev_jupyter_lab],
)
