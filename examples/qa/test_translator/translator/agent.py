"""Gherkin to JSON Translator - Translates .feature files to JSON test structures."""

import json
from datetime import UTC, datetime
from pathlib import Path

from gherkin.parser import Parser
from strands import Agent

from examples.qa.test_translator.translator.models import Feature

BASE_PATH = Path(__file__).parent


class TranslationError(Exception):
    """Exception raised when feature translation fails."""
    pass


def load_agent_prompt() -> str:
    """Load system prompt from local directory."""
    prompt_path = BASE_PATH / "system_prompt.md"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Agent prompt not found: {prompt_path}")
    return prompt_path.read_text()


def parse_gherkin_file(file_path: Path) -> dict:
    """Parse a .feature file into Gherkin AST."""
    parser = Parser()
    content = file_path.read_text()
    return parser.parse(content)


def resolve_test_url(tags: list, tag_url_map: dict) -> str:
    """Resolve test URL from feature tags."""
    for tag in tags:
        tag_name = tag.lstrip("@").lower()
        if tag_name in tag_url_map:
            return tag_url_map[tag_name]

    # Try default
    if "default" in tag_url_map:
        return tag_url_map["default"]

    raise ValueError(f"No URL mapping found for tags: {tags}")


def resolve_model_id(agent: Agent) -> str:
    """Extract the model ID from a Strands agent."""
    if hasattr(agent.model, "config"):
        return agent.model.config.get("model_id", "unknown")
    return "unknown"


def translate_feature_to_json(
    feature_path: Path, agent: Agent, tag_url_map: dict
) -> dict:
    """Translate a single .feature file to JSON structure.

    Args:
        feature_path: Path to the .feature file
        agent: Strands agent for translation
        tag_url_map: Mapping of tags to URLs

    Returns:
        Translated feature dictionary

    Raises:
        TranslationError: If translation or variable reference validation fails
    """
    print(f"  Translating {feature_path.name}...")

    try:
        # Parse Gherkin
        gherkin_ast = parse_gherkin_file(feature_path)

        # Translate using Strands agent with structured output
        ast_json = json.dumps(gherkin_ast, indent=2)
        prompt = f"""Translate this Gherkin AST to JSON test structure.

File: {feature_path.name}

Gherkin AST:
{ast_json}"""

        # Use structured_output_model for type-safe, validated response
        result = agent(prompt)
        test_feature_obj: Feature = result.structured_output
        
        if test_feature_obj is None:
            raise TranslationError(f"Agent failed to produce structured output for {feature_path.name}")

        # Add base_url from tags
        test_feature_obj.base_url = resolve_test_url(test_feature_obj.tags, tag_url_map)

        # Add metadata
        test_feature_obj.conversion_timestamp = datetime.now(UTC).isoformat()
        test_feature_obj.source_file = feature_path.name
        test_feature_obj.bedrock_model_id = resolve_model_id(agent)

        # Convert Pydantic model to dict after all properties are set
        feature_dict = test_feature_obj.model_dump()

        return feature_dict
    except Exception as e:
        raise


def save_feature_json(feature_data: dict, output_dir: Path, feature_name: str):
    """Save feature JSON to output directory."""
    output_path = output_dir / f"{feature_name}.json"
    with open(output_path, "w") as f:
        json.dump(feature_data, f, indent=2)
    print(f"    ✓ Saved to {output_path.name}")


def translate_all_features(
    *,
    input_dir: Path,
    output_dir: Path,
    tag_url_map: dict[str, str],
    bedrock_model_id: str | None,
) -> list[dict]:
    """Translate all Gherkin .feature files to JSON test structures.

    Args:
        input_dir: Directory containing .feature files.
        output_dir: Directory to write translated JSON files.
        tag_url_map: Mapping of Gherkin tags to starting URLs.
        bedrock_model_id: Bedrock model ID for the Strands agent.

    Returns:
        List of translated feature dictionaries.

    Raises:
        ValueError: If configuration is invalid or no features found.
        FileNotFoundError: If feature directory doesn't exist.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Validate input directory
    if not input_dir.exists() or not input_dir.is_dir():
        raise FileNotFoundError(f"Invalid feature directory: {input_dir}")

    if not tag_url_map:
        raise ValueError(
            "No URL mappings configured! Add GHERKIN_TAG_* or DEFAULT_TEST_URL to .env"
        )

    # Find .feature files
    feature_files = list(input_dir.glob("*.feature"))
    if not feature_files:
        raise ValueError(f"No .feature files found in {input_dir}")

    # Create translator agent
    system_prompt = load_agent_prompt()
    agent = Agent(
        name="gherkin_translator",
        model=bedrock_model_id,
        system_prompt=system_prompt,
        structured_output_model=Feature,
    )

    print(f"  Bedrock Model: {resolve_model_id(agent)}")
    print(f"  Feature Dir:   {input_dir}")
    print(f"  Output Dir:    {output_dir}")
    print(f"  URL Mappings:  {len(tag_url_map)} tag(s) configured")
    print(f"  Found {len(feature_files)} .feature file(s)")

    # Translate each feature
    translated_features = []
    for feature_file in feature_files:
        try:
            feature_data = translate_feature_to_json(feature_file, agent, tag_url_map)
            save_feature_json(feature_data, output_dir, feature_file.stem)
            translated_features.append(feature_data)
        except Exception as e:
            print(f"    ✗ Error translating {feature_file.name}: {e}")
            raise

    print(f"  ✓ Translated {len(translated_features)}/{len(feature_files)} feature(s)")
    return translated_features
