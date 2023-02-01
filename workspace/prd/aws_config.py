from phidata.aws.config import AwsConfig
from phidata.aws.resource.group import (
    AwsResourceGroup,
    DbInstance,
    DbSubnetGroup,
    EcsCluster,
    EcsContainer,
    EcsService,
    EcsTaskDefinition,
)

from workspace.prd.docker_config import prd_ml_server_image
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

# -*- ML database instance
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

# -*- ECS cluster
launch_type = "FARGATE"
prd_ecs_cluster = EcsCluster(
    name=f"{ws_settings.prd_key}-cluster",
    enabled=ws_settings.prd_ml_server_enabled,
    ecs_cluster_name=ws_settings.prd_key,
    capacity_providers=[launch_type],
    skip_create=skip_create,
    skip_delete=skip_delete,
    wait_for_creation=wait_for_create,
    wait_for_deletion=wait_for_delete,
)

# -*- ML Server Container
ml_server_container_port = 8000
prd_ml_server_container = EcsContainer(
    name=ws_settings.ws_name,
    enabled=ws_settings.prd_ml_server_enabled,
    image=prd_ml_server_image.get_image_str(),
    port_mappings=[{"containerPort": ml_server_container_port}],
    command=["api-prd"],
    environment=[
        {"name": "RUNTIME", "value": "prd"},
        # Database configuration
        # {"name": "WAIT_FOR_DB", "value": "True"},
        # {"name": "DB_HOST", "value": ""},
        # {"name": "DB_PORT", "value": "5432"},
        # {"name": "DB_USER", "value": prd_db_instance.get_master_username()},
        # {"name": "DB_PASS", "value": prd_db_instance.get_master_user_password()},
        # {"name": "DB_SCHEMA", "value": prd_db_instance.get_db_name()},
        # Upgrade database on startup
        # {"name": "UPGRADE_DB", "value": "True"},
    ],
    log_configuration={
        "logDriver": "awslogs",
        "options": {
            "awslogs-group": ws_settings.prd_key,
            "awslogs-region": ws_settings.aws_region,
            "awslogs-create-group": "true",
            "awslogs-stream-prefix": "ml-server",
        },
    },
)

# -*- ML Server Task Definition
prd_ml_server_task = EcsTaskDefinition(
    name=f"{ws_settings.prd_key}-td",
    family=ws_settings.prd_key,
    network_mode="awsvpc",
    cpu="512",
    memory="1024",
    containers=[prd_ml_server_container],
    requires_compatibilities=[launch_type],
    skip_create=skip_create,
    skip_delete=skip_delete,
    wait_for_creation=wait_for_create,
    wait_for_deletion=wait_for_delete,
)

# -*- ML Server Service
prd_ml_service = EcsService(
    name=f"{ws_settings.prd_key}-service",
    ecs_service_name=ws_settings.prd_key,
    desired_count=1,
    launch_type=launch_type,
    cluster=prd_ecs_cluster,
    task_definition=prd_ml_server_task,
    network_configuration={
        "awsvpcConfiguration": {
            "subnets": ws_settings.subnet_ids,
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
    ecs_clusters=[prd_ecs_cluster],
    ecs_task_definitions=[prd_ml_server_task],
    ecs_services=[prd_ml_service],
)

#
# -*- Define production AWS resources using the AwsConfig
#
prd_aws_config = AwsConfig(
    env=ws_settings.prd_env,
    resources=[prd_aws_resources],
)
