import logging
import sys
import os
from nova_act import NovaAct

# Configure logging for CloudWatch
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def handler(event, context):
    logger.info(f"Handler started - Event received: {event} with context: {context}")
    
    try:
        # Get API key from environment
        api_key = os.environ.get("NOVA_ACT_API_KEY")
        if not api_key:
            raise ValueError("NOVA_ACT_API_KEY environment variable is required")

        # Extract parameters with defaults
        default_prompt = "Find flights from Boston to Wolf on Feb 22nd"
        default_starting_page = "https://nova.amazon.com/act/gym/next-dot/search"
        if isinstance(event, dict):
            prompt = event.get("prompt", default_prompt)
            starting_page = event.get("starting_page", default_starting_page)
        else:
            prompt = default_prompt
            starting_page = default_starting_page

        logger.info("Starting Nova Act...")
        logger.info(f"Prompt: {prompt}")
        logger.info(f"Starting page: {starting_page}")

        with NovaAct(
            starting_page=starting_page,
            nova_act_api_key=api_key,
            headless=True,
            chrome_channel="chromium",
        ) as nova:
            logger.info("Invoking Nova Act")
            result = nova.act(prompt)
            logger.info(f"Nova Act result: {result}")
            
            return {
                "status": "success",
                "response": str(result),
                "prompt": prompt,
                "starting_page": starting_page
            }
            
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "status": "error", 
            "response": str(e),
            "prompt": event.get("prompt", "") if isinstance(event, dict) else "",
            "starting_page": event.get("starting_page", "") if isinstance(event, dict) else ""
        }
    finally:
        logger.info("Shutting down...")