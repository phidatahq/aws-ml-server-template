from phidata.app.postgres import PostgresDb
from phidata.app.server import ApiServer, AppServer
from phidata.docker.config import DockerConfig, DockerImage

from workspace.settings import ws_settings

#
# -*- Dev Docker resources
#

# -*- ML Server Image
dev_ml_server_image = DockerImage(
    name=f"{ws_settings.image_repo}/{ws_settings.ws_name}",
    tag=ws_settings.dev_env,
    # Use the pre-built image by default
    # enabled=False,
    # To build your own image, uncomment the following line
    enabled=(ws_settings.build_images and ws_settings.dev_ml_server_enabled),
    path=str(ws_settings.ws_dir.parent),
    # Manually specify the platform
    # platform="linux/amd64",
    dockerfile="Dockerfile",
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
)

# -*- Api Server running FastAPI on port 9090
dev_api_server = ApiServer(
    name=f"{ws_settings.ws_name}-api",
    enabled=ws_settings.dev_api_server_enabled,
    image=dev_ml_server_image,
    mount_workspace=True,
    use_cache=ws_settings.use_cache,
)

# -*- Postgres database used for dev data
dev_db = PostgresDb(
    name=f"{ws_settings.ws_name}-db",
    enabled=ws_settings.dev_postgres_enabled,
    db_user=ws_settings.ws_name,
    db_password=ws_settings.ws_name,
    db_schema=ws_settings.ws_name,
    # Connect to this db on port 9325
    container_host_port=9325,
)

#
# -*- Define dev Docker resources using the DockerConfig
#
dev_docker_config = DockerConfig(
    env=ws_settings.dev_env,
    network=ws_settings.ws_name,
    apps=[dev_api_server, dev_app_server, dev_db],
    images=[dev_ml_server_image],
)
