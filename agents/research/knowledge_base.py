"""Up-to-date market knowledge base for the Research Sub-Agent.

Data sourced from public earnings reports, analyst research, and industry publications.
Last updated: March 2026.
"""

# --- Platform Financial Performance ---

ZOMATO_FINANCIALS = {
    "entity_name": "Eternal (Zomato)",
    "fy25": {
        "revenue_crore": 20243,
        "revenue_yoy_growth_pct": 67,
        "net_profit_crore": 527,
        "profitable": True,
    },
    "q1_fy26": {
        "revenue_crore": 7167,
        "revenue_yoy_growth_pct": 70,
        "net_profit_crore": 25,
        "note": "Profit dip due to Blinkit investment phase",
    },
    "food_delivery": {
        "market_share_pct": 57,
        "monthly_transacting_users_crore": 2.09,
        "restaurant_partners": 270000,
        "take_rate_pct": 24.3,
    },
    "quick_commerce_blinkit": {
        "market_share_pct": 46,
        "daily_orders_lakh": 15.7,
        "aov_inr": 665,
        "revenue_yoy_growth_pct": 117,
        "contribution_margin_positive": True,
    },
    "b2b_hyperpure": {
        "partners_served": 40000,
        "cities": 100,
        "products": 4000,
        "q3_fy25_revenue_crore": 859,
        "growth_note": "Revenue grew ~1000% from Q1 FY22 (Rs 80 Cr) to Q3 FY25 (Rs 859 Cr)",
        "consecutive_double_digit_qoq_quarters": 8,
    },
}

SWIGGY_FINANCIALS = {
    "entity_name": "Swiggy",
    "fy25": {
        "revenue_crore": 15227,
        "revenue_yoy_growth_pct": 35,
        "net_loss_crore": 3117,
        "profitable": False,
    },
    "q1_fy26": {
        "revenue_crore": 4971,
        "revenue_yoy_growth_pct": 54,
        "net_loss_crore": 1197,
    },
    "ttm_revenue_crore": 20164,  # as of Feb 2026
    "food_delivery": {
        "market_share_pct": 43,
        "monthly_transacting_users_million": 17.8,
        "mtu_yoy_growth_pct": 25.3,
        "restaurant_partners": 300000,
        "cities": 500,
        "take_rate_pct": 25.4,
        "gmv_yoy_growth_pct": 19,
        "revenue_yoy_growth_pct": 22,
    },
    "quick_commerce_instamart": {
        "market_share_pct": 25,
        "daily_orders_lakh": 12.15,
        "aov_inr": 527,
        "gmv_yoy_growth_pct": 108,
        "qoq_growth_pct": 16,
        "revenue_yoy_growth_pct": 103,
    },
    "bolt_10min_delivery": {
        "share_of_total_delivery_pct": 12,
    },
    "profitability_guidance": {
        "qcommerce_cm_breakeven": "Q3 FY26",
        "adjusted_ebitda_breakeven": "Q2 FY27",
        "consolidated_adj_ebitda_positive": "Q3 FY26",
    },
    "valuation": {
        "revenue_multiple": 3.27,
        "discount_to_zomato_pct": 45,
    },
}

# --- Market Size & Industry Benchmarks ---

INDIA_FOOD_DELIVERY_MARKET = {
    "market_size_usd_billion_2025": 61.19,
    "cagr_pct_range": "14.2-27.3",
    "global_share_pct": 9.1,
    "top_5_global_market": True,
    "broader_foodservice_market_usd_billion_2030": 120,
    "delivery_channel_cagr_pct": 12.52,
    "dine_in_share_pct": 59.49,
}

KEY_BENCHMARKS = {
    "avg_order_value_inr": 400,
    "first_year_revenue_uplift_from_platform_pct": 42,
    "aov_delivery_vs_dinein_uplift_pct": 32,
    "ai_upsell_success_rate_pct": 28,
    "ai_dynamic_pricing_profit_uplift_pct": 12.5,
    "mobile_app_order_share_pct": 85.4,
    "digital_payment_share_pct": 91.7,
    "platform_commission_range_pct": "15-30",
    "effective_take_rate_pct": "24-25",
    "tier_2_3_order_share_pct": 48,
    "cloud_kitchens_urban_india": 20000,
}

# --- Commission Structure ---

COMMISSION_STRUCTURE = {
    "swiggy": {
        "commission_range_pct": "15-30",
        "take_rate_pct": 25.4,
        "setup_fee_inr": "10,000-20,000",
        "onboarding_fee_inr": 999,
        "platform_fee_per_order_inr": 10,
        "packaging_fee_per_order_inr": "5-15",
        "marketing_services_monthly_inr": "5,000-10,000",
    },
    "zomato": {
        "commission_range_pct": "15-30",
        "take_rate_pct": 24.3,
        "commission_cap_pct": 30,
        "platform_fee_per_order_inr": 10,
        "note": "Tiered models based on location, volume, and plan choice",
    },
}

# --- Competitive Landscape ---

COMPETITIVE_LANDSCAPE = [
    {
        "player": "Zomato/Eternal",
        "food_delivery_share_pct": 57,
        "quick_commerce_share_pct": 46,
        "differentiator": "Profitable, ecosystem (Hyperpure, District, Blinkit)",
    },
    {
        "player": "Swiggy",
        "food_delivery_share_pct": 43,
        "quick_commerce_share_pct": 25,
        "differentiator": "Unified platform, Bolt 10-min delivery, Dineout",
    },
    {
        "player": "Zepto",
        "food_delivery_share_pct": None,
        "quick_commerce_share_pct": 29,
        "differentiator": "Pure-play quick commerce, ~250 dark stores",
    },
    {
        "player": "Rapido",
        "food_delivery_share_pct": "Emerging",
        "quick_commerce_share_pct": None,
        "differentiator": "Flat-rate delivery (Rs 25-50), undercutting 20-30% commissions",
    },
]

# --- Growth Levers (Detailed) ---

GROWTH_LEVERS = {
    "menu_optimization": {
        "description": "Optimize menu for platform algorithms and customer conversion",
        "tactics": [
            "Keep online menus to 25-30 best dishes",
            "Use search-friendly keywords (e.g. 'spicy chicken wings', 'vegan pasta')",
            "Invest in high-quality food photography",
            "Optimize descriptions with selling points",
            "Use Swiggy's Menu Score Tool (score out of 100)",
        ],
    },
    "platform_advertising": {
        "description": "CPC campaigns for top placement in search results",
        "tactics": [
            "85%+ users choose from first 15 listings - ads ensure top placement",
            "Schedule ads during peak hours, not all-day",
            "Geo-target delivery-optimized zones",
            "Rotate offers every 7-10 days to avoid ad fatigue",
            "Starting budget Rs 50K-1L/month can push to 200 orders/day in 2 months",
            "Maintain ratings above 4.0 (Swiggy) / 3.5 (Zomato) before investing in ads",
        ],
    },
    "strategic_discounts": {
        "description": "Targeted promotions for visibility and volume",
        "tactics": [
            "Both platforms feature dedicated discount sections (auto visibility boost)",
            "Use flat discounts, combo deals (increase AOV), loyalty discounts",
            "Meal of the Day / Happy Hours for targeted time slots",
            "Participate in platform-led themed campaigns",
            "Trending dish identification led to 38% AOV increase in case studies",
        ],
    },
    "ratings_management": {
        "description": "Review management for algorithm ranking",
        "tactics": [
            "Keep negative reviews under 2%",
            "Respond professionally to all reviews",
            "Algorithm priority for restaurants with lowest prep times",
            "Better placement for restaurants in discount programs",
        ],
    },
    "pricing_strategy": {
        "description": "Smart pricing to balance margins and volume",
        "tactics": [
            "Don't uniformly increase prices by 30%+ to cover commissions",
            "Star dishes in high demand can absorb higher markups",
            "Add-ons (extra toppings, sides) significantly increase AOV",
            "AOV through delivery apps is 32% higher than dine-in on average",
            "AI-powered recommendations achieve 28% upsell success rate",
        ],
    },
    "operational_excellence": {
        "description": "Ops improvements for better ranking and customer satisfaction",
        "tactics": [
            "Fast prep time improves rankings and visibility",
            "Sturdy, branded packaging improves repeat orders",
            "Dedicated prep lines for digital orders",
            "Menu engineering for travel durability",
            "POS integration with Swiggy/Zomato for unified analytics",
        ],
    },
    "omnichannel_strategy": {
        "description": "Multi-channel approach for discovery and profitability",
        "tactics": [
            "Marketplace (Swiggy/Zomato) for discovery and reach",
            "Direct ordering for profitability and margin protection",
            "Loyalty programs to drive repeat behavior",
            "Social media to drive traffic to platform listings",
            "QR codes in physical locations linking to online ordering",
            "Local food blogger partnerships for visibility",
        ],
    },
    "geographic_expansion": {
        "description": "Expand into underserved delivery zones and tier 2/3 cities",
        "tactics": [
            "Cloud/ghost kitchens for new delivery zones (20K+ in urban India)",
            "Swiggy POP (meals Rs 99-200 with free delivery) for price-sensitive segments",
            "Tier 2/3 cities account for 48%+ of food delivery orders",
        ],
    },
    "platform_intelligence": {
        "description": "Leverage platform analytics tools for data-driven decisions",
        "tactics": [
            "Swiggy Market Intelligence Dashboard: business, ops, customer, funnel, spend metrics",
            "Zomato partner dashboard: order analytics, competitor benchmarks, ad performance",
            "Funnel tracking: page visits -> cart -> order (low conversion = menu/pricing issue)",
            "Use Hyperpure/Assure for supply chain cost optimization",
        ],
    },
}

# --- Onboarding Requirements ---

ONBOARDING_REQUIREMENTS = {
    "mandatory": [
        "FSSAI license (non-negotiable)",
        "PAN card",
        "Bank account details",
        "High-quality dish images for top 5 items",
    ],
    "optional": [
        "GST registration (mandatory if turnover above Rs 40 lakh)",
    ],
    "approval_timelines": {
        "zomato_days": "5-10 working days",
        "swiggy_days": "7-12 working days",
    },
}

# --- Key Industry Trends 2025-2026 ---

INDUSTRY_TRENDS = [
    "Quick commerce as primary battleground - 10-min grocery and food delivery",
    "AI/ML integration - personalized recommendations, dynamic pricing, logistics optimization",
    "Tier 2/3 city expansion - nearly half of orders now from outside metros",
    "Sustainability goals - Zomato targeting 100% EV deliveries by 2033",
    "Omnichannel restaurants - integration of dine-in, direct delivery, and aggregator channels",
    "B2B supply chain consolidation - Hyperpure and Assure competing for 80% unorganized market",
    "Autonomous/hybrid delivery - robots for short-radius, AI dispatch for route optimization",
]
