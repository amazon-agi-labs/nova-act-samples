# Amazon Nova Agent Examples

Examples demonstrating how to use Nova Act with the Nova API to build intelligent agents that combine UI automation with Amazon Nova models. These examples show how Nova Act's browser automation capabilities can be enhanced with Nova's multimodal AI to create powerful agentic workflows for web-based tasks.

## Repository Structure

```
├── travel_agent.py         # Travel destination research agent
├── book_research_agent.py  # Book discovery and analysis agent
├── financial_analyst.py    # Stock data extraction and analysis agent
├── requirements.txt        # Python dependencies
```

## Prerequisites

1. Complete the [Getting Started](../README.md#getting-started) section in the main examples directory
2. Install dependencies:
   ```bash
   pip install -r examples/nova_agents/requirements.txt
   ```
3. Generate a Nova API key at [nova.amazon.com/dev/api](https://nova.amazon.com/dev/api) and set it as an environment variable:
   ```bash
   export NOVA_API_KEY="your-api-key-here"
   ```

## Usage

### travel_agent.py - Travel Destination Research Agent

A Strands Agents implementation that uses Nova Act to extract destinations and generates travel recommendations using Nova's language capabilities.

```bash
# Run with default 5 destinations
python -m examples.nova_agents.travel_agent

# Run with custom number of destinations
python -m examples.nova_agents.travel_agent --num_destinations 3
```

**Implementation Details:**
- Strands integrated with Nova API for Nova model orchestration
- Nova Grounding to ground destination research with data from the web
- Nova Act as a tool for extracting destinations from the web
- Structured data extraction with Pydantic schemas
- Travel agent persona

### book_research_agent.py - Book Discovery and Analysis Agent

A literary research assistant that uses Nova Act to extract top books from websites and Nova model to analyze their popularity and recommend similar titles.

```bash
# Default
python -m examples.nova_agents.book_research_agent --website_url <url>

# Extract books with custom prompt
python -m examples.nova_agents.book_research_agent --website_url <url> --nova_act_prompt "Search for the best selling mystery novels"

# Extract custom number of books
python -m examples.nova_agents.book_research_agent --website_url <url> --num_books 5
```

**Implementation Details:**
- Nova Act for web scraping book data from any website
- Literary analysis using Nova's language understanding
- Book recommendation engine based on themes and appeal
- Structured book data extraction with Pydantic schemas
- Flexible Nova Act prompts for book discovery

> **Note:** The Nova Act prompt may need to be adjusted based on the website's structure and content.

### financial_analyst.py - Financial Data Extraction and Analysis Agent

A financial analyst that uses Nova Act to extract stock data from websites and Nova model to provide detailed insights into ticker performance and market trends.

```bash
# Default
python -m examples.nova_agents.financial_analyst --website_url <url>

# Custom Prompt
python -m examples.nova_agents.financial_analyst --website_url <url> --nova_act_prompt "Find top 5 companies by market cap"
```

**Implementation Details:**
- Nova Act for web scraping stock data from any financial website
- Stock performance analysis using Nova's language understanding
- Market insights focused on price movements and trends
- Structured stock data extraction with Pydantic schemas
- Flexible Nova Act prompts for financial data discovery

> **Note:** The Nova Act prompt should be tailored to the specific financial website's layout and data presentation

## Next Steps

- For additional Nova Agent examples, visit [this repository](https://github.com/amazon-nova-api/getting-started-with-nova-api/tree/main/examples/nova_agents)
- To learn more about the Nova API, check out the [getting started guide](https://github.com/amazon-nova-api/getting-started-with-nova-api)
- For production deployments, see [CDK →](../../cdk/README.md)
- For complete applications, see [Solutions →](../../solutions/README.md)
