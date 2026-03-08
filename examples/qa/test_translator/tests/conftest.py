"""Pytest configuration and fixtures for Nova Act tests."""

import os
import sys
from pathlib import Path

import pytest

from examples.nova_act_client import NovaActClient
from examples.qa.test_translator.config import AppConfig
from examples.qa.test_translator.config.exceptions import ConfigurationError
from examples.qa.test_translator.translator import translate_all_features


def pytest_configure(config):
    """Configure pytest with AppConfig and discover workflow definition."""
    try:
        config.app_config = AppConfig()  # type: ignore
    except ConfigurationError as e:
        # Print the error cleanly before pytest wraps it
        print(f"\n{e}", file=sys.stderr)
        pytest.exit("Configuration error - see message above", returncode=1)

    # Discover (or create) the workflow definition once per session

    s3_bucket_name = os.getenv("NOVA_ACT_S3_BUCKET_NAME", None)
    client = NovaActClient()
    client.discover_workflow_definition(
        name=config.app_config.workflow_definition_name,
        s3_bucket_name=s3_bucket_name,
    )


def pytest_sessionstart(session):
    """Run before all tests - translate features if TRANSLATE_FEATURES=true or no JSON files exist."""
    app_config = session.config.app_config
    features_dir = app_config.resolve_translated_feature_dir()

    # Check if any JSON files exist
    json_files = list(features_dir.glob("*.json")) if features_dir.exists() else []

    # Translate if explicitly enabled OR if no JSON files exist
    should_translate = app_config.translate_features or not json_files

    if not should_translate:
        return

    reason = (
        "TRANSLATE_FEATURES=true"
        if app_config.translate_features
        else "no translated features found"
    )
    print("\n" + "=" * 70)
    print(f"Translating Gherkin features ({reason})...")
    print("=" * 70)

    try:
        translate_all_features(
            input_dir=app_config.resolve_feature_dir(),
            output_dir=app_config.resolve_translated_feature_dir(),
            tag_url_map=app_config.get_tag_url_mapping(),
            bedrock_model_id=app_config.bedrock_model_id,
        )
        print("✓ Translation complete\n")
    except Exception as e:
        pytest.exit(f"Translation failed: {e}", returncode=1)


def collect_feature_files(features_dir: Path):
    """Collect all JSON feature files for parametrization."""
    json_files = list(features_dir.glob("*.json"))
    if not json_files:
        return []
    return [(json_file, json_file.stem) for json_file in json_files]


def pytest_generate_tests(metafunc):
    """Dynamically generate tests for each JSON feature file."""
    if "feature_file" in metafunc.fixturenames:
        app_config = metafunc.config.app_config
        features_dir = app_config.resolve_translated_feature_dir()
        feature_files = collect_feature_files(features_dir)

        if not feature_files:
            pytest.skip(f"No JSON files found in {features_dir}")

        # Parametrize with feature file path and test ID
        metafunc.parametrize(
            "feature_file,feature_name",
            feature_files,
            ids=[name for _, name in feature_files],
        )
