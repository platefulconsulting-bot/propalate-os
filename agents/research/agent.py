"""Research Sub-Agent for Swiggy & Zomato Sales Growth Intelligence.

This agent researches platform-specific sales data, market trends, and growth
metrics to help clients optimize their presence on Swiggy and Zomato.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Platform(Enum):
    SWIGGY = "swiggy"
    ZOMATO = "zomato"
    BOTH = "both"


class ClientCategory(Enum):
    RESTAURANTS = "restaurants"
    CLOUD_KITCHENS = "cloud_kitchens"
    QSR_CHAINS = "qsr_chains"
    GROCERY = "grocery"
    ENTERPRISE = "enterprise"


@dataclass
class PlatformMetrics:
    """Key performance metrics for a food delivery platform."""

    platform: str
    gross_merchandise_value: Optional[float] = None
    revenue: Optional[float] = None
    order_volume_monthly: Optional[int] = None
    average_order_value: Optional[float] = None
    active_restaurants: Optional[int] = None
    active_delivery_partners: Optional[int] = None
    cities_covered: Optional[int] = None
    market_share_pct: Optional[float] = None
    yoy_growth_pct: Optional[float] = None
    quick_commerce_revenue: Optional[float] = None


@dataclass
class GrowthReport:
    """Sales growth analysis report for a client."""

    client_name: str
    platform: str
    category: str
    metrics: PlatformMetrics
    growth_levers: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    competitive_insights: list[str] = field(default_factory=list)
    risk_factors: list[str] = field(default_factory=list)


# Industry knowledge base for the research agent
PLATFORM_KNOWLEDGE = {
    "swiggy": {
        "overview": (
            "Swiggy is one of India's leading food delivery platforms, "
            "also operating Instamart (quick commerce) and Dineout (dining out). "
            "Listed on NSE/BSE after IPO in late 2024."
        ),
        "key_metrics": {
            "cities": "680+",
            "restaurant_partners": "200,000+",
            "delivery_partners": "300,000+",
            "monthly_orders": "~55-60 million",
            "avg_order_value_inr": "350-450",
        },
        "growth_segments": [
            "Quick commerce (Instamart) - fastest growing vertical",
            "Swiggy One membership driving repeat orders",
            "Dineout integration for dine-in reservations",
            "Swiggy Genie for package delivery",
            "Corporate/B2B catering solutions",
        ],
        "sales_levers": [
            "Menu optimization and pricing strategy",
            "Visibility boosting through promoted listings",
            "Swiggy One partnership for priority placement",
            "Cloud kitchen expansion in underserved areas",
            "Festival and event-based promotional campaigns",
            "Data-driven demand forecasting",
        ],
    },
    "zomato": {
        "overview": (
            "Zomato is India's largest food delivery platform by market share, "
            "also operating Blinkit (quick commerce) and Hyperpure (B2B supplies). "
            "Publicly listed on NSE/BSE since 2021."
        ),
        "key_metrics": {
            "cities": "800+",
            "restaurant_partners": "250,000+",
            "delivery_partners": "350,000+",
            "monthly_orders": "~70-80 million",
            "avg_order_value_inr": "350-500",
        },
        "growth_segments": [
            "Blinkit quick commerce - major growth driver",
            "Zomato Gold membership for premium users",
            "Hyperpure B2B supply chain for restaurants",
            "District (going-out) platform for events/experiences",
            "Nugget - SaaS for restaurant management",
        ],
        "sales_levers": [
            "Zomato Pro/Gold visibility and ranking benefits",
            "Hyperpure supply chain cost optimization",
            "Restaurant dashboard analytics for menu engineering",
            "Promoted restaurant and ad placements",
            "Seasonal campaign participation",
            "Multi-location brand management",
        ],
    },
}

INDUSTRY_BENCHMARKS = {
    "food_delivery_india": {
        "market_size_usd_billions": "30-35 (2025 est.)",
        "cagr_pct": "25-30",
        "online_penetration_pct": "12-15",
        "top_players": ["Zomato", "Swiggy", "ONDC-based apps"],
        "key_trends": [
            "Quick commerce convergence with food delivery",
            "Private label brands by platforms",
            "AI-driven personalization and recommendations",
            "Tier 2/3 city expansion as primary growth driver",
            "Sustainability and green delivery initiatives",
            "Subscription/membership models driving loyalty",
        ],
    }
}


class ResearchAgent:
    """Sub-agent that researches Swiggy & Zomato sales growth for clients."""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.platform_knowledge = PLATFORM_KNOWLEDGE
        self.benchmarks = INDUSTRY_BENCHMARKS

    def get_platform_overview(self, platform: str) -> dict:
        """Get comprehensive overview of a platform."""
        platform = platform.lower()
        if platform == "both":
            return {
                "swiggy": self.platform_knowledge["swiggy"],
                "zomato": self.platform_knowledge["zomato"],
            }
        if platform not in self.platform_knowledge:
            raise ValueError(f"Unknown platform: {platform}. Use 'swiggy', 'zomato', or 'both'.")
        return self.platform_knowledge[platform]

    def get_growth_levers(self, platform: str, category: str = "restaurants") -> list[str]:
        """Get sales growth levers for a specific platform and client category."""
        platform = platform.lower()
        base_levers = self.platform_knowledge.get(platform, {}).get("sales_levers", [])

        category_specific = {
            "restaurants": [
                "Optimize menu photos and descriptions for higher conversion",
                "Implement dynamic pricing during peak/off-peak hours",
                "Leverage platform analytics for bestseller identification",
            ],
            "cloud_kitchens": [
                "Multi-brand strategy to capture different segments",
                "Location analytics for optimal kitchen placement",
                "Shared kitchen cost optimization",
            ],
            "qsr_chains": [
                "Franchise-level performance benchmarking",
                "Centralized menu management across locations",
                "Chain-wide promotional campaign coordination",
            ],
            "grocery": [
                "Quick commerce listing optimization",
                "Inventory sync for real-time availability",
                "Bundle deals and combo pricing strategy",
            ],
            "enterprise": [
                "Corporate catering and bulk order programs",
                "Dedicated account management setup",
                "Custom SLA and delivery commitments",
            ],
        }

        return base_levers + category_specific.get(category, [])

    def analyze_platform_growth(
        self, platform: str, client_category: str = "restaurants", client_name: str = ""
    ) -> GrowthReport:
        """Generate a comprehensive growth analysis report."""
        platform_data = self.get_platform_overview(platform)
        growth_levers = self.get_growth_levers(platform, client_category)

        metrics = PlatformMetrics(
            platform=platform,
            cities_covered=int(platform_data["key_metrics"]["cities"].replace("+", "")),
            active_restaurants=int(
                platform_data["key_metrics"]["restaurant_partners"]
                .replace("+", "")
                .replace(",", "")
            ),
        )

        recommendations = self._generate_recommendations(platform, client_category)
        competitive_insights = self._generate_competitive_insights(platform)
        risk_factors = self._identify_risks(platform, client_category)

        return GrowthReport(
            client_name=client_name or "Anonymous",
            platform=platform,
            category=client_category,
            metrics=metrics,
            growth_levers=growth_levers,
            recommendations=recommendations,
            competitive_insights=competitive_insights,
            risk_factors=risk_factors,
        )

    def compare_platforms(self) -> dict:
        """Compare Swiggy vs Zomato across key dimensions."""
        return {
            "market_leader": "Zomato (by order volume and market share)",
            "quick_commerce_leader": "Zomato (via Blinkit)",
            "b2b_supply_chain": "Zomato (via Hyperpure)",
            "dining_out": "Swiggy (via Dineout) vs Zomato (via District)",
            "membership_programs": {
                "swiggy": "Swiggy One",
                "zomato": "Zomato Gold",
            },
            "tech_saas": "Zomato (via Nugget restaurant SaaS)",
            "growth_rate": "Both growing 20-30% YoY in food delivery",
            "recommendation": (
                "Dual-platform presence recommended for maximum reach. "
                "Prioritize Zomato for volume, Swiggy for premium segments."
            ),
        }

    def get_industry_benchmarks(self) -> dict:
        """Return current industry benchmarks."""
        return self.benchmarks["food_delivery_india"]

    def _generate_recommendations(self, platform: str, category: str) -> list[str]:
        """Generate actionable recommendations based on platform and category."""
        common = [
            "Maintain dual-platform presence for maximum customer reach",
            "Invest in high-quality food photography and menu descriptions",
            "Participate in platform-led promotional events and campaigns",
            "Monitor and respond to customer reviews within 24 hours",
            "Use platform analytics dashboard for data-driven decisions",
        ]

        platform_specific = {
            "swiggy": [
                "Enroll in Swiggy One program for priority visibility",
                "Explore Instamart listing for grocery/essentials cross-sell",
                "Leverage Dineout for offline-to-online customer acquisition",
            ],
            "zomato": [
                "Use Hyperpure for supply chain cost reduction",
                "Explore Nugget SaaS for operational efficiency",
                "Participate in Zomato Gold for premium customer access",
            ],
        }

        return common + platform_specific.get(platform, [])

    def _generate_competitive_insights(self, platform: str) -> list[str]:
        """Generate competitive intelligence insights."""
        return [
            "ONDC-based food delivery apps emerging as potential disruptors with lower commissions",
            "Quick commerce (10-min delivery) becoming table stakes for all platforms",
            "Platform commission rates: 15-30% depending on tier and volume",
            "Subscription models driving 40-50% of repeat orders on both platforms",
            "AI-powered menu recommendations increasing average order value by 15-20%",
            "Tier 2/3 cities showing 2x growth rate compared to metros",
        ]

    def _identify_risks(self, platform: str, category: str) -> list[str]:
        """Identify potential risk factors."""
        return [
            "Platform commission increases can erode margins",
            "Algorithm changes may affect restaurant visibility unpredictably",
            "Intense competition from new entrants and ONDC ecosystem",
            "Rising delivery partner costs and regulatory pressure",
            "Customer acquisition cost inflation on platform ads",
            "Dependency on single platform creates concentration risk",
        ]
