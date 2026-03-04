# Propalate OS - AI Sub-Agents for Sales Intelligence

Sub-agent system for food delivery platform sales research and B2B sales automation.

## Agents

### 1. Research Sub-Agent (`agents/research/`)
Swiggy & Zomato sales growth intelligence agent for client advisory.

### 2. B2B Sales Sub-Agent (`agents/sales_b2b/`)
B2B sales and marketing automation agent with outreach, lead qualification, and pipeline management capabilities.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```python
from agents.research.agent import ResearchAgent
from agents.sales_b2b.agent import SalesB2BAgent

# Research agent
researcher = ResearchAgent()
report = researcher.analyze_platform_growth("swiggy", client_category="restaurants")

# B2B Sales agent
sales_agent = SalesB2BAgent()
leads = sales_agent.qualify_leads(platform="zomato", segment="enterprise")
```
