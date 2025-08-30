import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment
load_dotenv()

client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

SYSTEM = """You are the Analyst Agent. 
Your job is to evaluate startup/business ideas and provide market validation insights."""

def run_analyst_agent(schema_json: dict) -> dict:
    prompt = f"""
You are given a startup idea schema. Analyze it and return structured insights.

Idea Schema:
{json.dumps(schema_json, indent=2)}

Tasks:
1. Market overview (size, demand, recent trends)
2. Competition analysis (top players, gaps)
3. Business model validation (is it realistic?)
4. Key opportunities
5. Key risks
6. Suggested improvements

Return ONLY valid JSON with fields:
- market
- competition
- business_model
- opportunities
- risks
- improvements
"""

    resp = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        return json.loads(resp.content[0].text)
    except Exception:
        return {"error": "Failed to parse Claude output", "raw": resp.content[0].text}


if __name__ == "__main__":
    # Example test with Greetings Generator
    schema_example = {
        "idea_title": "Greetings Generator",
        "one_liner": "A microsaas product that allows users to create and send customized greetings.",
        "problem": "People struggle to find personalized greetings that resonate.",
        "target_customer": "Individuals and small businesses sending greetings.",
        "solution": "AI-powered personalized greeting generator.",
        "business_model": "Freemium with premium subscription.",
        "pricing": "$5/month premium",
        "gtm": "Social media, event partnerships",
        "competition": "Canva, greeting card apps",
        "moat": "AI personalization, local language support",
        "key_risks": "High competition, retention challenges"
    }

    report = run_analyst_agent(schema_example)
    print(json.dumps(report, indent=2))
