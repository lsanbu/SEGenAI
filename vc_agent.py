import os
import json
from typing import Dict, Any
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables (expects CLAUDE_API_KEY in .env or OS env)
load_dotenv()

# You can override the model via env VC_MODEL; otherwise use Sonnet 3.5
CLAUDE_MODEL = os.getenv("VC_MODEL", "claude-3-5-sonnet-20240620")
client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

SYSTEM = """You are the VC Agent. Think like an early-stage venture capitalist.
Given a startup's structured IdeaSchema, assess feasibility and fundability.

Output STRICT JSON ONLY with these fields:
- scalability: string (how big and scalable can this get? geo/segments/platforms)
- revenue_potential: string (directional TAM/SAM/SOM or realistic revenue paths)
- unit_economics: string (pricing logic, CAC/LTV intuition, margins, payback)
- risks: string[] (top 3–6 risks across product, GTM, team, capital, compliance)
- fundability_score: number (integer 1–5; 1=unfundable, 5=highly fundable)
- rationale: string (short justification for the score)

Rules:
- Always return valid JSON. No prose outside JSON.
- Be concise, practical, and investor-grade.
- If data is missing, make reasonable assumptions and mark them clearly.
"""

def run_vc_agent(schema_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Takes the Listener's IdeaSchema dict and returns a VC-style feasibility assessment.
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

    # Claude responses come as a list of content blocks; we expect text in [0].text
    text = ""
    try:
        text = resp.content[0].text
        return json.loads(text)
    except Exception as e:
        # Safe fallback with raw response included for debugging
        return {
            "error": f"Failed to parse VC Agent output: {e}",
            "raw": text or str(resp)
        }

if __name__ == "__main__":
    # Quick test with your Greetings Generator idea
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
    result = run_vc_agent(example_schema)
    print(json.dumps(result, indent=2, ensure_ascii=False))
