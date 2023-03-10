from phidata.aws.config import AwsConfig, AwsResourceGroup
from phidata.aws.resource.s3.bucket import S3Bucket

from workspace.settings import ws_settings

# -*- Define S3 bucket for dev data
dev_data_s3_bucket = S3Bucket(
    name=f"{ws_settings.dev_key}-data",
    acl="private",
    # Set True in production to skip deletion when running `phi ws down`
    skip_delete=False,
)

# -*- AwsResourceGroup for dev environment
dev_aws_resources = AwsResourceGroup(
    name=ws_settings.dev_key,
    s3_buckets=[dev_data_s3_bucket],
)

# -*- AwsConfig for dev environment
dev_aws_config = AwsConfig(
    env=ws_settings.dev_env,
    resources=[dev_aws_resources],
)
