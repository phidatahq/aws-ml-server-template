from phidata.aws.config import AwsConfig
from phidata.aws.resource.group import (
    AwsResourceGroup,
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

# -*- Create ECS cluster to run ML Apps
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

# -*- ML App Container running Streamlit on ECS
app_container_port = 9095
prd_app_container = EcsContainer(
    name=f"{ws_settings.ws_name}-app",
    enabled=ws_settings.prd_ml_server_enabled,
    image=prd_ml_server_image.get_image_str(),
    port_mappings=[{"containerPort": app_container_port}],
    command=["app start"],
    environment=[
        {"name": "RUNTIME", "value": "prd"},
    ],
    log_configuration={
        "logDriver": "awslogs",
        "options": {
            "awslogs-group": ws_settings.prd_key,
            "awslogs-region": ws_settings.aws_region,
            "awslogs-create-group": "true",
            "awslogs-stream-prefix": "app",
        },
    },
)

# -*- ML App Task Definition
prd_app_task_definition = EcsTaskDefinition(
    name=f"{ws_settings.prd_key}-td",
    family=ws_settings.prd_key,
    network_mode="awsvpc",
    cpu="512",
    memory="1024",
    containers=[prd_app_container],
    requires_compatibilities=[launch_type],
    skip_create=skip_create,
    skip_delete=skip_delete,
    wait_for_creation=wait_for_create,
    wait_for_deletion=wait_for_delete,
)

# -*- ML App Service
prd_app_service = EcsService(
    name=f"{ws_settings.prd_key}-service",
    ecs_service_name=ws_settings.prd_key,
    desired_count=1,
    launch_type=launch_type,
    cluster=prd_ecs_cluster,
    task_definition=prd_app_task_definition,
    network_configuration={
        "awsvpcConfiguration": {
            # "subnets": ws_settings.subnet_ids,
            # "securityGroups": ws_settings.security_groups,
            "assignPublicIp": "ENABLED",
        }
    },
    # force_delete=True,
    # force_new_deployment=True,
    skip_create=skip_create,
    skip_delete=skip_delete,
    wait_for_creation=wait_for_create,
    wait_for_deletion=wait_for_delete,
)

# -*- AwsResourceGroup
prd_aws_resources = AwsResourceGroup(
    name=ws_settings.prd_key,
    ecs_clusters=[prd_ecs_cluster],
    ecs_task_definitions=[prd_app_task_definition],
    ecs_services=[prd_app_service],
)

#
# -*- Define production AWS resources using the AwsConfig
#
prd_aws_config = AwsConfig(
    env=ws_settings.prd_env,
    resources=[prd_aws_resources],
)
