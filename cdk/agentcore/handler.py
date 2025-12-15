#!/usr/bin/env python3

"""
AgentCore Handler for Nova Act Workflows

This handler uses the @app.entrypoint decorator pattern required for AgentCore runtime.
"""

import logging
import sys
import os
import boto3
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.tools.browser_client import browser_session
from nova_act import NovaAct

# Configure logging for CloudWatch
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize the app
app = BedrockAgentCoreApp()

@app.route("/ping")
def ping() -> dict[str, str]:
    return {"status": "healthy"}


@app.entrypoint
def handler(payload):
    """
    AgentCore entrypoint handler for Nova Act workflows.
    
    Args:
        payload: The payload data passed to the handler
        
    Returns:
        dict: Response with status and result
    """
    logger.info(f"Handler started - Payload received: {payload}")
    
    try:
        # Get API key from environment
        api_key = os.environ.get('NOVA_ACT_API_KEY')
        if not api_key:
            raise ValueError("NOVA_ACT_API_KEY environment variable is required")
        
        # Extract parameters from payload
        default_prompt = "Find flights from Boston to Wolf on Feb 22nd"
        prompt = payload.get("prompt", default_prompt) if isinstance(payload, dict) else default_prompt
        default_starting_page = "https://nova.amazon.com/act/gym/next-dot/search"
        starting_page = payload.get("starting_page", default_starting_page) if isinstance(payload, dict) else default_starting_page
        
        logger.info("Starting Nova Act with AgentCore browser session...")
        logger.info(f"Prompt: {prompt}")
        logger.info(f"Starting page: {starting_page}")
        
        # Create browser session
        logger.info("Creating the browser session")
        # Get current AWS region from boto3 session, fallback to us-east-1
        session = boto3.Session()
        region = session.region_name or 'us-east-1'
        with browser_session(region) as client:
            logger.info("Created the browser session. Getting ws url and headers")
            ws_url, headers = client.generate_ws_headers()
            logger.info(f"ws_url is {ws_url}")
            logger.info(f"headers are {headers}")
            
            # Execute Nova Act workflow with API key
            with NovaAct(
                nova_act_api_key=api_key,
                starting_page=starting_page,
                headless=True,
                record_video=False,
                clone_user_data_dir=False,
                cdp_endpoint_url=ws_url,
                cdp_headers=headers,
            ) as nova_act:
                logger.info("Invoking Nova Act")
                result = nova_act.act(prompt)
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
            "prompt": payload.get("prompt", "") if isinstance(payload, dict) else "",
            "starting_page": payload.get("starting_page", "") if isinstance(payload, dict) else ""
        }
    finally:
        logger.info("Shutting down...")
        if "client" in locals():
            client.stop()
            logger.info("✅ Browser session terminated")

if __name__ == "__main__":
    app.run()
