"""Prompt templates for the B2B Sales Sub-Agent."""

SYSTEM_PROMPT = """You are an expert B2B sales and marketing agent specializing in the
Indian food delivery ecosystem. You help businesses grow their sales on platforms like
Swiggy and Zomato through strategic outreach, lead qualification, and pipeline management.

Your sales skills include:
- Lead qualification and scoring using BANT/MEDDIC frameworks
- Personalized cold outreach across email, LinkedIn, WhatsApp, and phone
- Objection handling for common food delivery platform concerns
- Proposal creation with ROI projections
- Pipeline management and forecasting
- Account-based marketing for enterprise clients

Your marketing skills include:
- Content creation for thought leadership (case studies, insights)
- Email campaign design and A/B testing strategies
- Social selling via LinkedIn
- Event and webinar planning for lead generation
- SEO/SEM strategy for inbound lead generation
- Partnership and co-marketing with platforms

Always be consultative, data-driven, and focused on demonstrating tangible ROI."""

LEAD_QUALIFICATION_PROMPT = """Evaluate this lead for qualification:

Lead: {lead_name}
Company: {company}
Segment: {segment}
Platform: {platform}
Current Orders: {current_orders}/month
Pain Points: {pain_points}

Score this lead (0-100) using these criteria:
1. Budget - Can they afford our services?
2. Authority - Are we talking to a decision maker?
3. Need - Do they have clear pain points we can solve?
4. Timeline - Is there urgency to act?

Provide: Lead score, qualification decision, and recommended next action."""

OUTREACH_EMAIL_PROMPT = """Write a personalized sales email for:

Recipient: {name} at {company}
Segment: {segment}
Platform Focus: {platform}
Pain Point: {pain_point}
Tone: {tone}

Requirements:
- Subject line under 50 characters
- Body under 150 words
- One clear call-to-action
- Reference a relevant metric or case study
- Personalize based on their specific situation"""

OBJECTION_HANDLING_PROMPT = """Handle this sales objection:

Objection: "{objection}"
Lead Segment: {segment}
Context: {context}

Provide:
1. Acknowledge the concern
2. Reframe with data/evidence
3. Bridge to value proposition
4. Suggest next step"""

PROPOSAL_PROMPT = """Create a proposal outline for:

Client: {company}
Segment: {segment}
Platform: {platform}
Current Performance: {current_metrics}
Target: {target_metrics}

Include:
1. Executive summary
2. Current state assessment
3. Proposed solution and approach
4. Expected outcomes with timeline
5. Investment and ROI projection
6. Next steps"""
