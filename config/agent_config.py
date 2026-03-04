"""Configuration for Propalate OS sub-agents."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LLMConfig:
    """LLM provider configuration."""

    provider: str = "anthropic"
    model: str = "claude-sonnet-4-6"
    max_tokens: int = 4096
    temperature: float = 0.3


@dataclass
class ResearchAgentConfig:
    """Configuration for the Research Sub-Agent."""

    name: str = "swiggy-zomato-research"
    description: str = "Sales growth research agent for Swiggy & Zomato platforms"
    llm: LLMConfig = field(default_factory=lambda: LLMConfig(temperature=0.2))
    platforms: list[str] = field(default_factory=lambda: ["swiggy", "zomato"])
    default_category: str = "restaurants"
    enable_web_search: bool = True
    cache_ttl_hours: int = 24


@dataclass
class SalesB2BAgentConfig:
    """Configuration for the B2B Sales Sub-Agent."""

    name: str = "b2b-sales-marketing"
    description: str = "B2B sales and marketing agent for food delivery platform partnerships"
    llm: LLMConfig = field(default_factory=lambda: LLMConfig(temperature=0.4))
    segments: list[str] = field(default_factory=lambda: ["smb", "mid_market", "enterprise"])
    outreach_channels: list[str] = field(
        default_factory=lambda: ["email", "linkedin", "phone", "whatsapp"]
    )
    lead_score_threshold: int = 50
    max_daily_outreach: int = 50


@dataclass
class PropalateConfig:
    """Root configuration for Propalate OS."""

    research_agent: ResearchAgentConfig = field(default_factory=ResearchAgentConfig)
    sales_b2b_agent: SalesB2BAgentConfig = field(default_factory=SalesB2BAgentConfig)
    default_llm: LLMConfig = field(default_factory=LLMConfig)
