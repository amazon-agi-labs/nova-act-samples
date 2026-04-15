"""Pytest configuration and fixtures for Nova Act tests."""

import json
import re
import sys
from pathlib import Path

import pytest

from examples.qa.test_translator.config import AppConfig
from examples.qa.test_translator.config.exceptions import ConfigurationError
from examples.qa.test_translator.translator import translate_all_features


def pytest_configure(config):
    """Configure pytest with AppConfig."""
    try:
        config.app_config = AppConfig()  # type: ignore
    except ConfigurationError as e:
        # Print the error cleanly before pytest wraps it
        print(f"\n{e}", file=sys.stderr)
        pytest.exit("Configuration error - see message above", returncode=1)


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


def collect_feature_scenarios(features_dir: Path):
    """Collect all scenarios from all JSON feature files for parametrization.

    Returns a list of (feature_file, scenario_index, test_id) tuples,
    one per scenario across all feature files.
    """
    json_files = sorted(features_dir.glob("*.json"))
    if not json_files:
        return []

    scenarios = []
    for json_file in json_files:
        with open(json_file) as f:
            feature_data = json.load(f)

        feature_name = json_file.stem
        for idx, scenario in enumerate(feature_data.get("scenarios", [])):
            scenario_name = scenario.get("name", f"scenario_{idx}")
            # Sanitize scenario name for test ID
            safe_scenario = re.sub(r"[^\w\s-]", "", scenario_name)
            safe_scenario = re.sub(r"[-\s]+", "_", safe_scenario).lower()
            test_id = f"{feature_name}::{safe_scenario}"
            scenarios.append((json_file, idx, test_id))

    return scenarios


def pytest_generate_tests(metafunc):
    """Dynamically generate one test per scenario across all JSON feature files."""
    if "feature_file" in metafunc.fixturenames:
        app_config = metafunc.config.app_config
        features_dir = app_config.resolve_translated_feature_dir()
        scenarios = collect_feature_scenarios(features_dir)

        if not scenarios:
            pytest.skip(f"No JSON files found in {features_dir}")

        metafunc.parametrize(
            "feature_file,scenario_index,test_id",
            scenarios,
            ids=[test_id for _, _, test_id in scenarios],
        )
