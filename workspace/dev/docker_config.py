from phidata.app.postgres import PostgresDb
from phidata.app.redis import Redis
from phidata.docker.config import DockerConfig, DockerContainer, DockerImage

from workspace.settings import ws_settings

#
# -*- Dev Docker resources
#

# -*- Postgres database
dev_db = PostgresDb(
    name=f"{ws_settings.ws_name}-db",
    enabled=ws_settings.dev_postgres_enabled,
    db_user=ws_settings.ws_name,
    db_password=ws_settings.ws_name,
    db_schema=ws_settings.ws_name,
    # Connect to this db on port 9315
    container_host_port=9315,
)

# -*- Redis cache
dev_redis = Redis(
    name=f"{ws_settings.ws_name}-redis",
    enabled=ws_settings.dev_redis_enabled,
    redis_password=ws_settings.ws_name,
    command=["redis-server", "--save", "60", "1"],
    container_host_port=9316,
)

# -*- Api Image
dev_api_image = DockerImage(
    name=f"{ws_settings.image_repo}/{ws_settings.ws_name}",
    tag=ws_settings.dev_env,
    enabled=ws_settings.build_images,
    path=str(ws_settings.ws_dir.parent),
    platform="linux/amd64",
    pull=ws_settings.force_pull_images,
    push_image=ws_settings.push_images,
    skip_docker_cache=ws_settings.skip_image_cache,
    use_cache=ws_settings.use_cache,
)

# -*- Api Container
dev_api_container = DockerContainer(
    name=f"{ws_settings.ws_name}-server",
    enabled=ws_settings.dev_api_enabled,
    image=dev_api_image.get_image_str(),
    command=["api-dev"],
    platform="linux/amd64",
    # detach=False,
    # stdout=True,
    # stderr=True,
    environment={
        "RUNTIME": "dev",
        # Database configuration
        "DB_HOST": dev_db.get_db_host_docker(),
        "DB_PORT": dev_db.get_db_port_docker(),
        "DB_USER": dev_db.get_db_user(),
        "DB_PASS": dev_db.get_db_password(),
        "DB_SCHEMA": dev_db.get_db_schema(),
        # Redis configuration
        "REDIS_HOST": dev_redis.get_db_host_docker(),
        "REDIS_PORT": dev_redis.get_db_port_docker(),
        "REDIS_PASS": dev_redis.get_db_password(),
        "REDIS_SCHEMA": "1",
        # Celery configuration
        "CELERY_REDIS_DB": "2",
        # Upgrade database on startup
        # "UPGRADE_DB": True,
        # Wait for database and redis to be ready
        "WAIT_FOR_DB": True,
        "WAIT_FOR_REDIS": True,
    },
    ports={
        "9090": "9090",
    },
    volumes={
        str(ws_settings.ws_dir.parent): {
            "bind": "/usr/local/app",
            "mode": "rw",
        },
    },
    use_cache=ws_settings.use_cache,
)

#
# -*- Define dev Docker resources using the DockerConfig
#
dev_docker_config = DockerConfig(
    env=ws_settings.dev_env,
    network=ws_settings.ws_name,
    apps=[dev_db, dev_redis],
    images=[dev_api_image],
    containers=[dev_api_container],
)
