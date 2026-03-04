"""Prompt templates for the Research Sub-Agent."""

SYSTEM_PROMPT = """You are a specialized research analyst focused on India's food delivery
market, specifically Swiggy and Zomato platforms. Your role is to help clients grow their
sales on these platforms by providing data-driven insights, market analysis, and actionable
recommendations.

Your expertise includes:
- Platform-specific sales growth strategies for Swiggy and Zomato
- Market trends and competitive dynamics in Indian food delivery
- Menu optimization and pricing strategies
- Quick commerce growth (Blinkit, Instamart)
- B2B supply chain insights (Hyperpure)
- Customer acquisition and retention metrics
- Restaurant performance benchmarking

Always provide specific, actionable insights backed by market data and platform knowledge.
Focus on helping clients increase revenue, optimize margins, and grow market share."""

GROWTH_ANALYSIS_PROMPT = """Analyze the sales growth opportunity for {client_name}
on {platform} platform.

Client Category: {category}
Current Metrics: {metrics}

Provide:
1. Platform-specific growth opportunities
2. Top 5 actionable recommendations ranked by impact
3. Competitive positioning analysis
4. Risk factors and mitigation strategies
5. 90-day growth action plan"""

PLATFORM_COMPARISON_PROMPT = """Compare Swiggy and Zomato for {client_name} in the
{category} segment.

Evaluate:
1. Which platform offers better visibility and reach
2. Commission structures and margin impact
3. Growth potential in target markets
4. Platform tools and support available
5. Recommendation for platform prioritization"""

MARKET_TRENDS_PROMPT = """Provide a current market trends briefing for the Indian food
delivery industry relevant to {category} businesses.

Cover:
1. Industry growth trajectory and key drivers
2. Quick commerce impact on traditional delivery
3. Technology trends (AI, personalization, automation)
4. Regulatory landscape and compliance requirements
5. Emerging opportunities and threats"""
