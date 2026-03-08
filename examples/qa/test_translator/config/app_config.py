"""Unified configuration for QA Test Translator."""

import os
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from examples.nova_act_client import NovaActClient

from .decorators import validate_app_config

BASE_PATH = Path(__file__).parent.parent
DOTENV_ENCODING = "utf-8"
DOTENV_PATH = BASE_PATH / ".env"


class BaseConfig(BaseSettings):
    """
    Base configuration class that inherits from Pydantic BaseSettings to validate env vars.
    This class is responsible for loading environment variables from a .env file and validating them.
    """

    model_config = SettingsConfigDict(
        env_file=DOTENV_PATH, env_file_encoding=DOTENV_ENCODING, extra="ignore"
    )

    @validate_app_config
    def __init__(self, **data):
        load_dotenv(DOTENV_PATH, override=True, encoding=DOTENV_ENCODING)
        super().__init__(**data)


class AppConfig(BaseConfig):
    """
    Unified configuration for test execution and translation.
    Defines all environment variables required to run the QA Test Translator.
    """

    # Test Execution Settings
    translate_features: bool = Field(
        default=False,
        description="Auto-translate Gherkin features before running tests",
    )

    workflow_definition_name: str = Field(
        default=NovaActClient.DEFAULT_WORKFLOW_NAME,
        alias="NOVA_ACT_WORKFLOW_DEFINITION_NAME",
        description="Nova Act Workflow definition name",
    )

    headless: bool = Field(
        default=False,
        alias="HEADLESS",
        description="Run browser in headless mode",
    )

    # Translation Settings
    bedrock_model_id: str | None = Field(
        default=None,
        alias="BEDROCK_MODEL_ID",
        description="Bedrock model ID for test translation",
    )

    feature_dir: Path = Field(
        default=Path("features"),
        alias="FEATURE_DIR",
        description="Directory containing Gherkin .feature files",
    )

    translated_feature_dir: Path = Field(
        default=Path("features_translated"),
        alias="TRANSLATED_FEATURE_DIR",
        description="Directory for translated JSON test files",
    )

    default_test_url: str | None = Field(
        default=None,
        alias="DEFAULT_TEST_URL",
        description="Default URL when no tag mapping exists",
    )

    def get_tag_url_mapping(self) -> Dict[str, str]:
        """Extract GHERKIN_TAG_* environment variables into a mapping."""
        tag_url_map = {}
        for key, value in os.environ.items():
            if key.startswith("GHERKIN_TAG_"):
                tag_name = key.replace("GHERKIN_TAG_", "").lower()
                tag_url_map[tag_name] = value

        if self.default_test_url:
            tag_url_map["default"] = self.default_test_url

        return tag_url_map

    def resolve_feature_dir(self) -> Path:
        """Resolve feature directory to absolute path."""
        if self.feature_dir.is_absolute():
            return self.feature_dir
        return (BASE_PATH / self.feature_dir).resolve()

    def resolve_translated_feature_dir(self) -> Path:
        """Resolve translated feature directory to absolute path."""
        if self.translated_feature_dir.is_absolute():
            return self.translated_feature_dir
        return (BASE_PATH / self.translated_feature_dir).resolve()
