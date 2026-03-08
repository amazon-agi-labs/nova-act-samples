"""Gherkin to JSON translator CLI.

Converts .feature files into structured JSON that downstream consumers can
execute or process. Configurable via CLI arguments or .env file.

Usage:
python -m examples.qa.test_translator.translator.main \
  --feature_dir features/ \
  --output_dir features_translated/ \
  --tag search=https://example.com \
  --tag login=https://example.com/login
"""

import os
from pathlib import Path

import fire
from dotenv import load_dotenv

from examples.qa.test_translator.translator.agent import translate_all_features
from examples.utils import get_logger

LOGGER = get_logger(__name__)

_SCRIPT_DIR = Path(__file__).parent.parent
_DOTENV_PATH = _SCRIPT_DIR / ".env"


def main(
    feature_dir: str | None = None,
    output_dir: str | None = None,
    tag: list[str] | None = None,
    default_url: str | None = None,
    model_id: str | None = None,
) -> None:
    """Translate Gherkin .feature files to Nova Act JSON.

    All arguments fall back to values from .env if not provided via CLI.

    Args:
        feature_dir: Directory containing .feature files (relative to test_translator/).
        output_dir: Directory to write translated JSON (relative to test_translator/).
        tag: Tag-to-URL mappings as key=value pairs (e.g., search=https://example.com).
        default_url: Fallback URL when no tag mapping matches.
        model_id: Bedrock model ID for the Strands translation agent.
    """
    # Load .env if present so GHERKIN_TAG_* and other vars are available
    load_dotenv(_DOTENV_PATH, override=True)

    resolved_feature_dir = _resolve_path(
        feature_dir or os.getenv("FEATURE_DIR", "features")
    )
    resolved_output_dir = _resolve_path(
        output_dir or os.getenv("TRANSLATED_FEATURE_DIR", "features_translated")
    )
    resolved_model_id = model_id or os.getenv("BEDROCK_MODEL_ID", None)

    tag_url_map = _build_tag_url_map(
        tag or [], default_url or os.getenv("DEFAULT_TEST_URL")
    )

    LOGGER.info(f"Translating features from {resolved_feature_dir}")

    features = translate_all_features(
        input_dir=resolved_feature_dir,
        output_dir=resolved_output_dir,
        tag_url_map=tag_url_map,
        bedrock_model_id=resolved_model_id,
    )

    LOGGER.info(
        f"✓ Translation complete: {len(features)} feature(s) → {resolved_output_dir}"
    )


def _resolve_path(path: str) -> Path:
    """Resolve a path relative to the test_translator directory if not absolute."""
    p = Path(path)
    if p.is_absolute():
        return p
    return (_SCRIPT_DIR / p).resolve()


def _build_tag_url_map(tags: list[str], default_url: str | None) -> dict[str, str]:
    """Build tag-to-URL mapping from CLI args and GHERKIN_TAG_* env vars."""
    tag_url_map: dict[str, str] = {}

    # Pick up GHERKIN_TAG_* from environment
    for key, value in os.environ.items():
        if key.startswith("GHERKIN_TAG_"):
            tag_name = key.replace("GHERKIN_TAG_", "").lower()
            tag_url_map[tag_name] = value

    # CLI --tag flags override env vars
    for entry in tags:
        if "=" not in entry:
            raise ValueError(f"Invalid tag format '{entry}', expected key=url")
        key, url = entry.split("=", 1)
        tag_url_map[key.lower()] = url

    if default_url:
        tag_url_map["default"] = default_url

    return tag_url_map


if __name__ == "__main__":
    fire.Fire(main)
