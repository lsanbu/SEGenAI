import os
import json
from dotenv import load_dotenv

# Load .env (OPENAI_API_KEY, CLAUDE_API_KEY)
load_dotenv()

# Import your agents
from llm_agent import propose_next_step   # Listener Agent
from schema_types import IdeaSchema
from analyst_agent import run_analyst_agent   # Analyst Agent

def run_orchestrator(raw_idea: str):
    print("\n===== Listener Agent (Intake) =====")
    # Start with empty schema
    schema = IdeaSchema()
    chat_history = []

    # Step 1: Listener Agent fills schema
    listener_output = propose_next_step(raw_idea, schema, chat_history)
    schema_data = listener_output["current_schema"]

    print(json.dumps(schema_data, indent=2))

    print("\n===== Analyst Agent (Research + Validation) =====")
    # Step 2: Analyst Agent validates schema
    analyst_report = run_analyst_agent(schema_data)

    print(json.dumps(analyst_report, indent=2))

    return schema_data, analyst_report


if __name__ == "__main__":
    idea = "I want to build a microsaas product Greetings Generator so that anyone can send customized greetings instead of readymade ones."
    schema, report = run_orchestrator(idea)
