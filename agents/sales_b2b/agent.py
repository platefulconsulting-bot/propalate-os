"""B2B Sales Sub-Agent with Sales and Marketing Skills.

This agent handles B2B sales workflows including lead qualification, outreach
automation, pipeline management, and marketing campaign support for food delivery
platform partnerships.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class LeadStage(Enum):
    PROSPECT = "prospect"
    QUALIFIED = "qualified"
    CONTACTED = "contacted"
    MEETING_SCHEDULED = "meeting_scheduled"
    PROPOSAL_SENT = "proposal_sent"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class LeadSegment(Enum):
    SMB = "smb"
    MID_MARKET = "mid_market"
    ENTERPRISE = "enterprise"


class OutreachChannel(Enum):
    EMAIL = "email"
    LINKEDIN = "linkedin"
    PHONE = "phone"
    WHATSAPP = "whatsapp"
    IN_PERSON = "in_person"


@dataclass
class Lead:
    """A B2B sales lead."""

    name: str
    company: str
    segment: str
    platform: str  # swiggy, zomato, or both
    stage: str = LeadStage.PROSPECT.value
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    city: Optional[str] = None
    current_monthly_orders: Optional[int] = None
    target_monthly_orders: Optional[int] = None
    pain_points: list[str] = field(default_factory=list)
    score: int = 0  # 0-100 lead score


@dataclass
class OutreachMessage:
    """A generated outreach message."""

    channel: str
    subject: str
    body: str
    call_to_action: str
    personalization_notes: list[str] = field(default_factory=list)


@dataclass
class SalesPipeline:
    """Sales pipeline summary."""

    total_leads: int = 0
    qualified_leads: int = 0
    active_deals: int = 0
    pipeline_value_inr: float = 0.0
    conversion_rate_pct: float = 0.0
    avg_deal_cycle_days: int = 0
    leads_by_stage: dict = field(default_factory=dict)


# Sales playbooks for different segments
SALES_PLAYBOOKS = {
    "smb": {
        "description": "Small and medium restaurants, single-location businesses",
        "ideal_customer_profile": {
            "monthly_orders": "500-5,000",
            "locations": "1-3",
            "revenue_range_inr": "5L-50L/month",
            "pain_points": [
                "Low visibility on platform",
                "High commission rates eating margins",
                "No dedicated account manager",
                "Struggling with menu optimization",
                "Inconsistent order volumes",
            ],
        },
        "value_proposition": (
            "We help small restaurants grow their platform sales by 30-50% through "
            "data-driven menu optimization, visibility strategies, and promotional campaigns."
        ),
        "sales_cycle_days": 14,
        "outreach_sequence": [
            {"day": 1, "channel": "email", "action": "Introduction with case study"},
            {"day": 3, "channel": "whatsapp", "action": "Follow-up with quick win tip"},
            {"day": 5, "channel": "phone", "action": "Discovery call"},
            {"day": 7, "channel": "email", "action": "Proposal with ROI projection"},
            {"day": 10, "channel": "phone", "action": "Objection handling / negotiation"},
            {"day": 14, "channel": "in_person", "action": "Close meeting"},
        ],
    },
    "mid_market": {
        "description": "Multi-location restaurants, regional chains, cloud kitchens",
        "ideal_customer_profile": {
            "monthly_orders": "5,000-50,000",
            "locations": "3-20",
            "revenue_range_inr": "50L-5Cr/month",
            "pain_points": [
                "Inconsistent performance across locations",
                "Need for centralized analytics",
                "Brand consistency challenges",
                "Supply chain cost optimization",
                "Scaling operations efficiently",
            ],
        },
        "value_proposition": (
            "We provide multi-location performance optimization, centralized analytics, "
            "and platform strategy that drives 20-40% growth across all outlets."
        ),
        "sales_cycle_days": 30,
        "outreach_sequence": [
            {"day": 1, "channel": "linkedin", "action": "Connect with decision maker"},
            {"day": 3, "channel": "email", "action": "Industry insights report"},
            {"day": 7, "channel": "phone", "action": "Discovery call with stakeholders"},
            {"day": 14, "channel": "email", "action": "Custom audit report"},
            {"day": 21, "channel": "in_person", "action": "Presentation to leadership"},
            {"day": 28, "channel": "email", "action": "Proposal and negotiation"},
        ],
    },
    "enterprise": {
        "description": "National QSR chains, large cloud kitchen operators, F&B conglomerates",
        "ideal_customer_profile": {
            "monthly_orders": "50,000+",
            "locations": "20+",
            "revenue_range_inr": "5Cr+/month",
            "pain_points": [
                "Platform dependency and negotiation leverage",
                "Data integration with internal systems",
                "Brand control and customization",
                "Multi-platform strategy optimization",
                "Advanced analytics and forecasting",
            ],
        },
        "value_proposition": (
            "Enterprise-grade platform strategy, custom analytics, and dedicated support "
            "to maximize ROI across Swiggy, Zomato, and emerging platforms."
        ),
        "sales_cycle_days": 60,
        "outreach_sequence": [
            {"day": 1, "channel": "linkedin", "action": "Warm intro via mutual connection"},
            {"day": 5, "channel": "email", "action": "Thought leadership content"},
            {"day": 10, "channel": "phone", "action": "Executive briefing request"},
            {"day": 20, "channel": "in_person", "action": "On-site assessment"},
            {"day": 35, "channel": "email", "action": "Detailed proposal with case studies"},
            {"day": 45, "channel": "in_person", "action": "C-suite presentation"},
            {"day": 55, "channel": "email", "action": "Contract negotiation"},
        ],
    },
}

# Marketing campaign templates
MARKETING_TEMPLATES = {
    "cold_email_intro": {
        "subject": "Grow your {platform} sales by {growth_pct}% - here's how",
        "body": (
            "Hi {name},\n\n"
            "I noticed {company} has been doing well on {platform}, but based on our "
            "analysis of similar {category} businesses in {city}, there's potential to "
            "grow your orders by {growth_pct}%.\n\n"
            "We recently helped a similar restaurant increase their monthly orders from "
            "{benchmark_before} to {benchmark_after} using our platform optimization strategies.\n\n"
            "Would you be open to a 15-minute call this week to discuss how we can "
            "help {company} achieve similar results?\n\n"
            "Best,\n{sender_name}"
        ),
    },
    "case_study_followup": {
        "subject": "How {case_study_company} grew {metric} on {platform}",
        "body": (
            "Hi {name},\n\n"
            "Following up on my previous message. I wanted to share how "
            "{case_study_company} achieved {result} on {platform}.\n\n"
            "Key highlights:\n"
            "- {highlight_1}\n"
            "- {highlight_2}\n"
            "- {highlight_3}\n\n"
            "I'd love to create a similar success story for {company}. "
            "Can we schedule a quick call?\n\n"
            "Best,\n{sender_name}"
        ),
    },
    "linkedin_connection": {
        "message": (
            "Hi {name}, I work with {category} businesses to optimize their presence "
            "on Swiggy and Zomato. Would love to connect and share some insights "
            "relevant to {company}."
        ),
    },
    "whatsapp_quick_tip": {
        "message": (
            "Hi {name}! Quick tip for {company} on {platform}: "
            "{tip}. This alone can boost orders by {impact_pct}%. "
            "Happy to share more insights - let me know if you'd like a quick call."
        ),
    },
}


class SalesB2BAgent:
    """Sub-agent for B2B sales and marketing workflows."""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.playbooks = SALES_PLAYBOOKS
        self.templates = MARKETING_TEMPLATES
        self.pipeline: list[Lead] = []

    def qualify_leads(
        self, platform: str = "both", segment: str = "smb", min_score: int = 50
    ) -> list[Lead]:
        """Score and qualify leads based on segment criteria."""
        qualified = []
        for lead in self.pipeline:
            if platform != "both" and lead.platform != platform:
                continue
            if lead.segment != segment:
                continue
            lead.score = self._calculate_lead_score(lead, segment)
            if lead.score >= min_score:
                lead.stage = LeadStage.QUALIFIED.value
                qualified.append(lead)
        return sorted(qualified, key=lambda l: l.score, reverse=True)

    def add_lead(self, lead: Lead) -> Lead:
        """Add a new lead to the pipeline."""
        lead.score = self._calculate_lead_score(lead, lead.segment)
        self.pipeline.append(lead)
        return lead

    def generate_outreach(
        self, lead: Lead, template_name: str = "cold_email_intro", **kwargs
    ) -> OutreachMessage:
        """Generate a personalized outreach message for a lead."""
        template = self.templates.get(template_name)
        if not template:
            raise ValueError(f"Unknown template: {template_name}")

        merge_fields = {
            "name": lead.name,
            "company": lead.company,
            "platform": lead.platform,
            "city": lead.city or "your city",
            "category": lead.segment,
            **kwargs,
        }

        subject = template.get("subject", "")
        body = template.get("body") or template.get("message", "")

        # Safe format - only replace keys that exist
        for key, value in merge_fields.items():
            subject = subject.replace(f"{{{key}}}", str(value))
            body = body.replace(f"{{{key}}}", str(value))

        channel = "email" if "subject" in template else "linkedin"
        if template_name == "whatsapp_quick_tip":
            channel = "whatsapp"

        return OutreachMessage(
            channel=channel,
            subject=subject,
            body=body,
            call_to_action="Schedule a discovery call",
            personalization_notes=[
                f"Lead segment: {lead.segment}",
                f"Platform: {lead.platform}",
                f"Stage: {lead.stage}",
            ],
        )

    def get_sales_playbook(self, segment: str) -> dict:
        """Get the sales playbook for a specific segment."""
        if segment not in self.playbooks:
            raise ValueError(f"Unknown segment: {segment}. Use 'smb', 'mid_market', or 'enterprise'.")
        return self.playbooks[segment]

    def get_outreach_sequence(self, segment: str) -> list[dict]:
        """Get the recommended outreach sequence for a segment."""
        playbook = self.get_sales_playbook(segment)
        return playbook["outreach_sequence"]

    def get_pipeline_summary(self) -> SalesPipeline:
        """Get a summary of the current sales pipeline."""
        leads_by_stage = {}
        for lead in self.pipeline:
            leads_by_stage[lead.stage] = leads_by_stage.get(lead.stage, 0) + 1

        qualified = [l for l in self.pipeline if l.score >= 50]
        active_stages = {
            LeadStage.CONTACTED.value,
            LeadStage.MEETING_SCHEDULED.value,
            LeadStage.PROPOSAL_SENT.value,
            LeadStage.NEGOTIATION.value,
        }
        active = [l for l in self.pipeline if l.stage in active_stages]
        won = [l for l in self.pipeline if l.stage == LeadStage.CLOSED_WON.value]

        total = len(self.pipeline)
        conversion = (len(won) / total * 100) if total > 0 else 0.0

        return SalesPipeline(
            total_leads=total,
            qualified_leads=len(qualified),
            active_deals=len(active),
            conversion_rate_pct=round(conversion, 1),
            leads_by_stage=leads_by_stage,
        )

    def advance_lead_stage(self, lead: Lead) -> Lead:
        """Move a lead to the next stage in the pipeline."""
        stage_order = [s.value for s in LeadStage]
        current_idx = stage_order.index(lead.stage) if lead.stage in stage_order else 0
        if current_idx < len(stage_order) - 2:  # Skip closed_lost
            lead.stage = stage_order[current_idx + 1]
        return lead

    def get_marketing_templates(self) -> dict:
        """Return all available marketing templates."""
        return {name: list(template.keys()) for name, template in self.templates.items()}

    def _calculate_lead_score(self, lead: Lead, segment: str) -> int:
        """Calculate a lead score (0-100) based on fit criteria."""
        score = 0

        # Platform presence (20 pts)
        if lead.platform == "both":
            score += 20
        elif lead.platform in ("swiggy", "zomato"):
            score += 15

        # Contact info completeness (20 pts)
        if lead.contact_email:
            score += 10
        if lead.contact_phone:
            score += 10

        # Pain points identified (20 pts)
        score += min(len(lead.pain_points) * 5, 20)

        # Order volume fit (20 pts)
        if lead.current_monthly_orders:
            icp = self.playbooks.get(segment, {}).get("ideal_customer_profile", {})
            orders_range = icp.get("monthly_orders", "0-0")
            min_orders = int(orders_range.split("-")[0].replace(",", "").replace("+", ""))
            if lead.current_monthly_orders >= min_orders:
                score += 20
            elif lead.current_monthly_orders >= min_orders * 0.5:
                score += 10

        # City presence (10 pts)
        if lead.city:
            score += 10

        # Growth ambition (10 pts)
        if lead.target_monthly_orders and lead.current_monthly_orders:
            if lead.target_monthly_orders > lead.current_monthly_orders:
                score += 10

        return min(score, 100)
