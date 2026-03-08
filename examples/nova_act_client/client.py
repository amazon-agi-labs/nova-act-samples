"""Nova Act Client Wrapper.

Provides a clean interface for Nova Act WorkflowDefinition operations.
Handles workflow discovery, creation, and management with proper error handling.

Note: Nova Act WorkflowDefinitions must be created in us-east-1 region.
"""

import os

import boto3
from mypy_boto3_nova_act.client import NovaActServiceClient
from mypy_boto3_nova_act.type_defs import (
    GetWorkflowDefinitionResponseTypeDef,
    WorkflowExportConfigTypeDef,
)
from mypy_boto3_s3.client import S3Client
from mypy_boto3_sts.client import STSClient

from examples.utils import get_logger

LOGGER = get_logger(__name__)

_DEFAULT_BUCKET_PREFIX = "nova-act-workflow-logs"


def _default_s3_bucket_name() -> str:
    """Build a default S3 bucket name from the current AWS identity.

    Format: nova-act-workflow-logs-{account_id}-{region}
    """
    session = boto3.Session()
    sts: STSClient = session.client("sts")
    account_id = sts.get_caller_identity()["Account"]
    region = session.region_name or "us-east-1"
    return f"{_DEFAULT_BUCKET_PREFIX}-{account_id}-{region}"


def _ensure_s3_bucket_exists(bucket_name: str) -> None:
    """Create the S3 bucket if it doesn't already exist."""
    from botocore.exceptions import ClientError

    s3: S3Client = boto3.client("s3")
    try:
        s3.head_bucket(Bucket=bucket_name)
        LOGGER.debug(f"S3 bucket already exists: {bucket_name}")
    except ClientError as e:
        error_code = str(e.response.get("Error", {}).get("Code", ""))
        if error_code in ("404", "NoSuchBucket"):
            LOGGER.info(f"Creating S3 bucket: {bucket_name}")
            s3.create_bucket(Bucket=bucket_name)
            LOGGER.info(f"✓ Created S3 bucket: {bucket_name}")
        else:
            raise


class NovaActClient:
    """Client for Nova Act WorkflowDefinition operations.

    Note: Nova Act WorkflowDefinitions are only available in us-east-1 region.
    """

    DEFAULT_MODEL_ID = "nova-act-latest"
    DEFAULT_WORKFLOW_NAME = "nova-act-examples"

    def __init__(self):
        """Initialize Nova Act client in us-east-1 (only supported region)."""
        self.client: NovaActServiceClient = boto3.client(
            "nova-act", region_name="us-east-1"
        )

    def create_workflow_definition(
        self,
        name: str,
        description: str | None = None,
        s3_bucket_name: str | None = None,
        s3_key_prefix: str | None = None,
    ) -> str:
        """Create a WorkflowDefinition.

        Args:
            name: WorkflowDefinition name
            description: Optional description
            s3_bucket_name: S3 bucket name for workflow export logs. If None, uses a
                default bucket name derived from the AWS account ID and region.
            s3_key_prefix: Optional S3 key prefix within the bucket

        Returns:
            WorkflowDefinition ARN
        """
        bucket_name = s3_bucket_name or _default_s3_bucket_name()
        _ensure_s3_bucket_exists(bucket_name)
        LOGGER.info(f"Creating WorkflowDefinition: '{name}' (bucket: {bucket_name})")

        export_config: WorkflowExportConfigTypeDef = {"s3BucketName": bucket_name}
        if s3_key_prefix:
            export_config["s3KeyPrefix"] = s3_key_prefix

        kwargs: dict = {"name": name, "exportConfig": export_config}
        if description:
            kwargs["description"] = description

        self.client.create_workflow_definition(**kwargs)

        # create_workflow_definition response doesn't include ARN; fetch it
        get_response = self.get_workflow_definition(name)
        arn = get_response["arn"]
        LOGGER.info(f"Created WorkflowDefinition: '{name}' ({arn})")
        return arn

    def get_workflow_definition(
        self, name: str
    ) -> GetWorkflowDefinitionResponseTypeDef:
        """Get a WorkflowDefinition by name.

        Args:
            name: WorkflowDefinition name

        Returns:
            WorkflowDefinition details
        """
        return self.client.get_workflow_definition(workflowDefinitionName=name)

    def discover_workflow_definition(
        self,
        name: str,
        s3_bucket_name: str | None = None,
        s3_key_prefix: str | None = None,
    ) -> str:
        """Auto-discover WorkflowDefinition — returns ARN if exists, creates if not.

        Args:
            name: WorkflowDefinition name
            s3_bucket_name: S3 bucket name for workflow export logs (used only on creation).
                If None, uses a default bucket name derived from the AWS account ID and region.
            s3_key_prefix: Optional S3 key prefix (used only on creation)

        Returns:
            WorkflowDefinition ARN
        """
        try:
            response = self.get_workflow_definition(name)
            arn = response["arn"]
            LOGGER.debug(f"Discovered WorkflowDefinition: '{name}' ({arn})")
            return arn
        except self.client.exceptions.ResourceNotFoundException:
            LOGGER.info(f"WorkflowDefinition '{name}' not found, creating...")
            return self.create_workflow_definition(
                name=name,
                description="Auto-discovered Nova Act workflow definition",
                s3_bucket_name=s3_bucket_name,
                s3_key_prefix=s3_key_prefix,
            )

    @staticmethod
    def get_workflow_kwargs() -> dict:
        """Return kwargs for the Nova Act SDK Workflow given the environment configuration.

        Reads NOVA_ACT_API_KEY, NOVA_ACT_WORKFLOW_DEFINITION_NAME, and NOVA_ACT_MODEL_ID
        from the environment. API key takes precedence — when set, workflow definition
        discovery is skipped. Model ID defaults to NovaActClient.DEFAULT_MODEL_ID.
        """
        api_key = os.getenv("NOVA_ACT_API_KEY", None)
        model_id = os.getenv("NOVA_ACT_MODEL_ID", NovaActClient.DEFAULT_MODEL_ID)

        kwargs: dict = {"model_id": model_id}

        if api_key:
            kwargs["nova_act_api_key"] = api_key
        else:
            workflow_definition_name = os.getenv(
                "NOVA_ACT_WORKFLOW_DEFINITION_NAME",
                NovaActClient.DEFAULT_WORKFLOW_NAME,
            )
            s3_bucket_name = os.getenv("NOVA_ACT_S3_BUCKET_NAME", None)
            client = NovaActClient()
            client.discover_workflow_definition(
                name=workflow_definition_name, s3_bucket_name=s3_bucket_name
            )
            kwargs["workflow_definition_name"] = workflow_definition_name

        return kwargs
