from phidata.aws.config import AwsConfig
from phidata.aws.resource.group import (
    AwsResourceGroup,
    CacheCluster,
    CacheSubnetGroup,
    DbInstance,
    DbSubnetGroup,
    EcsCluster,
    EcsContainer,
    EcsService,
    EcsTaskDefinition,
)

from workspace.prd.docker_config import prd_api_image
from workspace.settings import ws_settings

#
# -*- Production AWS resources
#

# -*- Settings
# Do not create the resource when running `phi ws up`
skip_create: bool = False
# Do not delete the resource when running `phi ws down`
skip_delete: bool = False
# Wait for the resource to be created
wait_for_create: bool = True
# Wait for the resource to be deleted
wait_for_delete: bool = True

# -*- RDS Database Subnet Group
prd_db_subnet_group = DbSubnetGroup(
    name=f"{ws_settings.prd_key}-db-sg",
    enabled=ws_settings.prd_postgres_enabled,
    subnet_ids=ws_settings.subnet_ids,
    skip_create=skip_create,
    skip_delete=skip_delete,
    wait_for_creation=wait_for_create,
    wait_for_deletion=wait_for_delete,
)

# -*- Elasticache Subnet Group
prd_redis_subnet_group = CacheSubnetGroup(
    name=f"{ws_settings.prd_key}-cache-sg",
    enabled=ws_settings.prd_redis_enabled,
    subnet_ids=ws_settings.subnet_ids,
    skip_create=skip_create,
    skip_delete=skip_delete,
    wait_for_creation=wait_for_create,
    wait_for_deletion=wait_for_delete,
)

# -*- Backend database instance
db_engine = "postgres"
prd_db_instance = DbInstance(
    name=f"{ws_settings.prd_key}-db",
    engine=db_engine,
    enabled=ws_settings.prd_postgres_enabled,
    engine_version="14.5",
    allocated_storage=100,
    # NOTE: For production, use a larger instance type.
    # Last checked price: $0.152 per hour = ~$110 per month
    db_instance_class="db.m6g.large",
    availability_zone=ws_settings.aws_az1,
    db_subnet_group=prd_db_subnet_group,
    enable_performance_insights=True,
    vpc_security_group_ids=ws_settings.security_groups,
    secrets_file=ws_settings.ws_dir.joinpath("secrets/prd_postgres_secrets.yml"),
    skip_create=skip_create,
    skip_delete=skip_delete,
    wait_for_creation=wait_for_create,
    wait_for_deletion=wait_for_delete,
)

# -*- Redis cache
prd_redis_cluster = CacheCluster(
    name=f"{ws_settings.prd_key}-cache",
    engine="redis",
    enabled=ws_settings.prd_redis_enabled,
    num_cache_nodes=1,
    # NOTE: For production, use a larger instance type.
    # Last checked price: $0.068 per hour = ~$50 per month
    cache_node_type="cache.m6g.large",
    security_group_ids=ws_settings.security_groups,
    cache_subnet_group=prd_redis_subnet_group,
    preferred_availability_zone=ws_settings.aws_az1,
    skip_create=skip_create,
    skip_delete=skip_delete,
    wait_for_creation=wait_for_create,
    wait_for_deletion=wait_for_delete,
)

# -*- ECS cluster
launch_type = "FARGATE"
prd_ecs_cluster = EcsCluster(
    name=f"{ws_settings.prd_key}-cluster",
    enabled=ws_settings.prd_api_enabled,
    ecs_cluster_name=ws_settings.prd_key,
    capacity_providers=[launch_type],
    skip_create=skip_create,
    skip_delete=skip_delete,
    wait_for_creation=wait_for_create,
    wait_for_deletion=wait_for_delete,
)

# -*- Api Container
api_container_port = 8000
prd_api_container = EcsContainer(
    name=f"{ws_settings.ws_name}-{ws_settings.image_suffix}",
    enabled=ws_settings.prd_api_enabled,
    image=prd_api_image.get_image_str(),
    port_mappings=[{"containerPort": api_container_port}],
    command=["api-prd"],
    environment=[
        {"name": "RUNTIME", "value": "prd"},
        {"name": "WAIT_FOR_DB", "value": "True"},
        {"name": "WAIT_FOR_REDIS", "value": "True"},
        # {"name": "UPGRADE_DB", "value": "True"},
        # Database configuration
        {
            "name": "DB_HOST",
            "value": "backend-prd-db-a.cuqtj11ky8hc.us-east-1.rds.amazonaws.com",
        },
        {"name": "DB_PORT", "value": "5432"},
        {"name": "DB_USER", "value": prd_db_instance.get_master_username()},
        {"name": "DB_PASS", "value": prd_db_instance.get_master_user_password()},
        {"name": "DB_SCHEMA", "value": prd_db_instance.get_db_name()},
        # Redis configuration
        {
            "name": "REDIS_HOST",
            "value": "backend-prd-cache.kymr3h.0001.use1.cache.amazonaws.com",
        },
        {"name": "REDIS_PORT", "value": "6379"},
        # {"name": "REDIS_PASS", "value": ""},
        {"name": "REDIS_SCHEMA", "value": "1"},
        # {"name": "REDIS_DRIVER", "value": "rediss"},
        # Celery configuration
        {"name": "CELERY_REDIS_DB", "value": "2"},
    ],
    log_configuration={
        "logDriver": "awslogs",
        "options": {
            "awslogs-group": ws_settings.prd_key,
            "awslogs-region": ws_settings.aws_region,
            "awslogs-create-group": "true",
            "awslogs-stream-prefix": "api",
        },
    },
)

# -*- Api Task Definition
prd_api_task = EcsTaskDefinition(
    name=f"{ws_settings.prd_key}-api-td",
    family=f"{ws_settings.prd_key}-{ws_settings.image_suffix}",
    network_mode="awsvpc",
    cpu="512",
    memory="1024",
    containers=[prd_api_container],
    requires_compatibilities=[launch_type],
    skip_create=skip_create,
    skip_delete=skip_delete,
    wait_for_creation=wait_for_create,
    wait_for_deletion=wait_for_delete,
)

# -*- Api Service
prd_api_service = EcsService(
    name=f"{ws_settings.prd_key}-api-service",
    ecs_service_name=f"{ws_settings.prd_key}-{ws_settings.image_suffix}",
    desired_count=3,
    launch_type=launch_type,
    cluster=prd_ecs_cluster,
    task_definition=prd_api_task,
    load_balancers=[
        {
            "targetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:@@@:targetgroup/@@@-tg/@@@",  # noqa: E501
            "containerName": prd_api_container.name,
            "containerPort": api_container_port,
        }
    ],
    network_configuration={
        "awsvpcConfiguration": {
            "subnets": ws_settings.public_subnets,
            "securityGroups": ws_settings.security_groups,
            "assignPublicIp": "ENABLED",
        }
    },
    force_delete=True,
    force_new_deployment=True,
    skip_create=skip_create,
    skip_delete=skip_delete,
    wait_for_creation=wait_for_create,
    wait_for_deletion=wait_for_delete,
)

# -*- AwsResourceGroup
prd_aws_resources = AwsResourceGroup(
    name=ws_settings.prd_key,
    db_subnet_groups=[prd_db_subnet_group],
    db_instances=[prd_db_instance],
    cache_subnet_groups=[prd_redis_subnet_group],
    cache_clusters=[prd_redis_cluster],
    ecs_clusters=[prd_ecs_cluster],
    ecs_task_definitions=[prd_api_task],
    ecs_services=[prd_api_service],
)

#
# -*- Define production AWS resources using the AwsConfig
#
prd_aws_config = AwsConfig(
    env=ws_settings.prd_env,
    resources=[prd_aws_resources],
)
