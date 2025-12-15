import logging
import sys
import os
from nova_act import NovaAct

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting Nova Act Fargate workflow...")

    try:
        # Get API key from environment
        api_key = os.environ.get("NOVA_ACT_API_KEY")
        if not api_key:
            raise ValueError("NOVA_ACT_API_KEY environment variable is required")

        # Set default values
        default_prompt = "Find flights from Boston to Wolf on Feb 22nd"
        default_starting_page = "https://nova.amazon.com/act/gym/next-dot/search"

        # Use environment variables or defaults
        prompt = os.environ.get("NOVA_ACT_PROMPT", default_prompt)
        starting_page = os.environ.get("NOVA_ACT_STARTING_PAGE", default_starting_page)

        logger.info(f"Prompt: {prompt}")
        logger.info(f"Starting page: {starting_page}")

        with NovaAct(
            starting_page=starting_page,
            nova_act_api_key=api_key,
            headless=True,
            record_video=False,
            clone_user_data_dir=False,
        ) as nova_act:
            logger.info("Invoking Nova Act")
            result = nova_act.act(prompt)
            logger.info(f"Nova Act result: {result}")

        logger.info("Fargate task completed successfully")

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        import traceback

        traceback.print_exc()
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


if __name__ == "__main__":
    main()
