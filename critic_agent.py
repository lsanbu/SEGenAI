import os
import json
from typing import Dict, Any
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables (expects CLAUDE_API_KEY in .env or OS env)
load_dotenv()

# You can override the model via env CRITIC_MODEL; otherwise uses Sonnet 3.5 by default.
# Tip: set CRITIC_MODEL to a newer Claude model in your .env when available.
CLAUDE_MODEL = os.getenv("CRITIC_MODEL", "claude-3-5-sonnet-20240620")
client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

SYSTEM = """You are the Critic Agent. Be a rigorous, fair devil’s advocate.
Given a startup's structured IdeaSchema, identify blind spots and risks across
regulation/compliance, technical feasibility, go-to-market, operations, and data/privacy.

Return STRICT JSON ONLY with these fields:
- regulatory: string (key compliance/ IP/ policy issues, including platform policies)
- technical: string (core build risks, scalability/latency, reliability, cost)
- gtm: string (distribution, differentiation, pricing, retention)
- operational: string (support, localization, seasonality, staffing)
- data_privacy: string (PII handling, content ownership, data residency)
- severity_ranking: string[] (array of keys in descending severity, choose from:
  ["gtm","regulatory","technical","operational","data_privacy"])
- mitigation: { "items": [ { "issue": string, "actions": string[] } ] }

Rules:
- Always return valid JSON, no prose outside JSON.
- Be concrete and actionable; avoid generic advice.
- If info is missing, make reasonable assumptions and mark them clearly.
"""

def run_critic_agent(schema_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Takes the Listener's IdeaSchema dict and returns a structured critique focusing on challenges.
    """
    user_prompt = f"""
You are given this IdeaSchema for a startup:

{json.dumps(schema_json, indent=2, ensure_ascii=False)}

Return ONLY the JSON object with the exact fields described by the system.
"""
    resp = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1200,
        temperature=0.5,
        system=SYSTEM,
        messages=[{"role": "user", "content": user_prompt}]
    )

    text = ""
    try:
        text = resp.content[0].text
        return json.loads(text)
    except Exception as e:
        # Safe fallback with raw response included for debugging
        return {
            "error": f"Failed to parse Critic Agent output: {e}",
            "raw": text or str(resp)
        }

if __name__ == "__main__":
    # Quick test with your Greetings Generator schema
    example_schema = {
        "idea_title": "Greetings Generator",
        "one_liner": "A micro-SaaS to create and send AI-personalized greetings.",
        "problem": "Generic templates lack personal resonance; creation is time-consuming.",
        "target_customer": "Individuals and SMBs sending seasonal/event-based greetings.",
        "solution": "AI-generated text+visual greetings with scheduling, language/localization.",
        "business_model": "Freemium; $5–$10/month premium; B2B team plans; credits for image gen.",
        "pricing": "$0 free tier, $9/month Pro, team $29/month.",
        "gtm": "Social media ads, influencer bundles, festival promos, WhatsApp/Telegram bots.",
        "competition": "Canva, American Greetings, JibJab, template marketplaces.",
        "moat": "Deep personalization, multi-lingual/local-festival packs, messaging app integrations.",
        "key_risks": "Churn, low willingness to pay, crowded space, seasonality."
    }

    result = run_critic_agent(example_schema)
    print(json.dumps(result, indent=2, ensure_ascii=False))
