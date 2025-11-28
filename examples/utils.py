"""
Utility functions for examples
"""

import logging
import os
from typing import get_args

from nova_act.types.workflow import ModelId


def get_logger(name: str):
  """
  Creates and configures a common logger for each example.
  """
  logger = logging.getLogger(name)
  logging.basicConfig(
      level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  )
  return logger

def get_workflow_kwargs():
  """
  Returns the kwargs for the Nova Act @workflow decorator given the environment configuration.
  """
  api_key = os.getenv("NOVA_ACT_API_KEY", None)
  workflow_definition_name = os.getenv("NOVA_ACT_WORKFLOW_DEFINITION_NAME", None)

  return {
    "model_id": get_args(ModelId)[0],
    "nova_act_api_key": api_key,
    "workflow_definition_name": workflow_definition_name
  }

