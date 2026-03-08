"""Extract data from Excel files and populate a form.

Demonstrates reading Excel data with a custom tool and populating web forms.

Usage:
python -m examples.tool_use.excel.form_fill [--file_name <excel_file>] [--row_number <row>]
"""

from pathlib import Path

import fire
import pandas as pd
from nova_act import NovaAct, SecurityOptions, tool, workflow
from pydantic import BaseModel

from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)


@tool
def read_row_as_dict(file_path: str, row_number: int) -> dict:
    """
    Reads a specific row from an Excel file and returns it as a dictionary where
    column headers are keys and row values are the corresponding dictionary values.

    Args:
        file_path (str): The path to the Excel file.
        row_number (int): The row number (1-based index) to retrieve.

    Returns:
        dict: A dictionary containing the data from the specified row.
    """
    # Read the Excel file using pandas with openpyxl engine
    df = pd.read_excel(file_path, engine="openpyxl")

    # Check if the row_number is within the valid range
    if row_number < 1 or row_number > len(df):
        raise ValueError(
            f"Row number {row_number} is out of range. The sheet has {len(df)} rows."
        )

    # Get the row data as a dictionary
    row_data = df.iloc[row_number - 1].to_dict()

    return row_data


class Person(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str


# Get the directory where our data files are stored
SCRIPT_DIR = Path(__file__).parent
DATA_FILES_DIR = str((SCRIPT_DIR / "data_files").absolute())


@workflow(**NovaActClient.get_workflow_kwargs())
def main(file_name: str = "people.xlsx", row_number: int = 1):
    """Extract data from Excel files and populate a form.

    Args:
        file_name: Excel file name (default: people.xlsx)
        row_number: Row number to read (1-3, default: 1)
    """
    if row_number not in [1, 2, 3]:
        row_number = 1

    file_uri = Path(f"{DATA_FILES_DIR}/{file_name}").as_uri()

    prompt = f"""
    Read the data from row number {row_number} in the Excel file {file_uri} in the current folder.
    Enter this data into the appropriate fields of the web form on the page, and then submit the form.

    Return the data that you read from the Excel file.
    """
    with NovaAct(
        starting_page=f"file://{DATA_FILES_DIR}/contact_order_form.html",
        security_options=SecurityOptions(
            allowed_file_open_paths=[f"{DATA_FILES_DIR}/*"]
        ),
        ignore_https_errors=True,
        tools=[read_row_as_dict],
    ) as nova:
        result = nova.act_get(prompt, schema=Person.model_json_schema())
        person_data = Person.model_validate(result.parsed_response)
        LOGGER.info(f"✓ Task completed: \n{person_data}")


if __name__ == "__main__":
    fire.Fire(main)
