# Amazon Nova Act Excel Tool Use Examples

Examples demonstrating how to use custom tools with Excel files.

## Repository Structure

```
├── data_files/             # Excel files and HTML forms for testing
└── form_fill.py            # Excel data to form example
```

## Prerequisites

Complete the [Getting Started](../../README.md#getting-started) section in the main examples directory before running these examples.

## Usage Instructions

### form_fill.py - Excel Data to Form

Demonstrates reading Excel data and populating web forms using custom tools.

```bash
python -m examples.tool_use.excel.form_fill
```

**Features:**
- Custom `read_row_as_dict()` tool for Excel file reading
- Loads local HTML form (`data_files/contact_order_form.html`)
- Automated form population from Excel data
- Supports multiple Excel files and row selection
- Returns validated person data using Pydantic models

**Examples:**
```bash
# Use defaults (people.xlsx, row 1)
python -m examples.tool_use.excel.form_fill

# Specify file and row
python -m examples.tool_use.excel.form_fill --file_name people-2.xlsx --row_number 2
```

## Next Steps

- Learn more about tools in the [README →](../README.md)
- For production deployments, see [CDK →](../../../cdk/README.md)
- For complete applications, see [Solutions →](../../../solutions/README.md)
- Visit the [Nova Act documentation →](https://docs.aws.amazon.com/nova-act)