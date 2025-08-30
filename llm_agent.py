import os
import json
from typing import Dict, Any, List
from openai import OpenAI
from schema_types import IdeaSchema

def get_client():
    """Return a fresh OpenAI client using the env var."""
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM = """You are the Idea Validation & Enrichment Agent.
Your job is to take a startup idea (typed, doc, or audio) and map it into the IdeaSchema below.

Rules:
- ALWAYS fill every field with best-guess text. Never leave null.
- If unclear, make a reasonable assumption and add "(please confirm)".
- Output ONLY valid JSON. No explanations, no extra text.

IdeaSchema fields:
idea_title, one_liner, problem, target_customer, solution, business_model,
pricing, gtm, competition, moat, key_risks.
"""

TOOL_DEF = [{
    "type": "function",
    "function": {
        "name": "emit_followup_or_schema",
        "description": "Either ask next follow-up or return final schema when complete.",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["need_followup", "complete"]},
                "question": {"type": "string", "description": "Ask only if need_followup"},
                "missing_field": {"type": "string", "description": "Schema key the question targets"},
                "current_schema": {"type": "object"}
            },
            "required": ["status", "current_schema"]
        }
    }
}]

def _messages(aggregated_text: str, current_schema: Dict[str, Any], chat_history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    base = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"Aggregated input:\n\n{aggregated_text}\n\nCurrent schema (JSON):\n{json.dumps(current_schema, ensure_ascii=False)}"}
    ]
    for m in chat_history[-8:]:
        base.append(m)
    return base

def propose_next_step(aggregated_text: str, schema_obj: IdeaSchema, chat_history: List[Dict[str, str]]):
    client = get_client()
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": aggregated_text}
    ]
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7
    )

    try:
        content = resp.choices[0].message.content
        schema_data = json.loads(content)   # expect JSON
        return {
            "status": "complete",
            "current_schema": schema_data
        }
    except Exception as e:
        return {
            "status": "complete",
            "current_schema": schema_obj.model_dump(),
            "error": f"Could not parse schema: {e}"
        }

    args = json.loads(tool_call.function.arguments or "{}")
    current = args.get("current_schema", {})
    schema_new = IdeaSchema(**{k: v for k, v in current.items() if k in IdeaSchema.model_fields})

    return {
        "status": "complete",   # 🔑 always complete
        "current_schema": schema_new.model_dump()
    }

    args = json.loads(tool_call.function.arguments or "{}")
    current = args.get("current_schema", {})
    schema_new = IdeaSchema(**{k: v for k, v in current.items() if k in IdeaSchema.model_fields})

    return {
        "status": "complete",
        "current_schema": schema_new.model_dump()
    }

    args = json.loads(tool_call.function.arguments or "{}")
    current = args.get("current_schema", {})
    schema_new = IdeaSchema(**{k: v for k, v in current.items() if k in IdeaSchema.model_fields})
    status = args.get("status", "need_followup")
    question = args.get("question")
    missing_field = args.get("missing_field")
    return {
        "status": status,
        "question": question,
        "missing_field": missing_field,
        "current_schema": schema_new.model_dump()
    }
