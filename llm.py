import json
import streamlit as st
import google.generativeai as genai

# ── Load API Key safely ────────────────────────────────────────────────────────
api_key = st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    # DO NOT crash import, just store None and handle later
    client = None
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

PROMPT_TEMPLATE = """
You are an AI assistant that extracts structured action items from meeting transcripts.

Analyze the transcript and extract:
1. summary
2. decisions
3. tasks
4. risks

Return ONLY valid JSON in this exact format:

{{
  "summary": "string",
  "decisions": ["string"],
  "tasks": [
    {{
      "task": "string",
      "assigned_to": "string",
      "deadline": "string",
      "priority": "High | Medium | Low",
      "notes": "string"
    }}
  ],
  "risks": ["string"]
}}

Rules:
- Return only valid JSON.
- Do not include markdown.
- Do not include explanations.
- If no owner is mentioned, use "Unassigned".
- If no deadline is mentioned, use "Not specified".
- If no clear priority is mentioned, use "Medium".
- Only include real action items.
- Keep the summary short, maximum 2 sentences.
- Add risks for tasks missing owner or deadline.
- If there are no decisions, return an empty list.
- If there are no tasks, return an empty list.

Transcript:
{transcript}
"""


def clean_model_output(raw_text: str) -> str:
    """
    Removes accidental markdown code fences if the model returns them.
    """
    text = raw_text.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    return text


def apply_fallbacks(data: dict) -> dict:
    """
    Ensures output always has the expected structure.
    """
    if not isinstance(data, dict):
        data = {}

    if "summary" not in data or not isinstance(data["summary"], str):
        data["summary"] = "No summary generated."

    if "decisions" not in data or not isinstance(data["decisions"], list):
        data["decisions"] = []

    if "tasks" not in data or not isinstance(data["tasks"], list):
        data["tasks"] = []

    if "risks" not in data or not isinstance(data["risks"], list):
        data["risks"] = []

    fixed_tasks = []

    for task in data["tasks"]:
        if not isinstance(task, dict):
            continue

        fixed_task = {
            "task": str(task.get("task", "Unnamed task")).strip() or "Unnamed task",
            "assigned_to": str(task.get("assigned_to", "Unassigned")).strip() or "Unassigned",
            "deadline": str(task.get("deadline", "Not specified")).strip() or "Not specified",
            "priority": str(task.get("priority", "Medium")).strip() or "Medium",
            "notes": str(task.get("notes", "")).strip()
        }

        # Normalize priority
        if fixed_task["priority"] not in {"High", "Medium", "Low"}:
            fixed_task["priority"] = "Medium"

        fixed_tasks.append(fixed_task)

        # Auto-add risks
        if fixed_task["assigned_to"] == "Unassigned":
            risk = f"Task '{fixed_task['task']}' has no clear owner."
            if risk not in data["risks"]:
                data["risks"].append(risk)

        if fixed_task["deadline"] == "Not specified":
            risk = f"Task '{fixed_task['task']}' has no clear deadline."
            if risk not in data["risks"]:
                data["risks"].append(risk)

    data["tasks"] = fixed_tasks
    return data


def extract_tasks(transcript: str) -> dict:
    """
    Converts transcript text into structured JSON using Gemini.
    """
    if not transcript or not transcript.strip():
        return {
            "summary": "No transcript provided.",
            "decisions": [],
            "tasks": [],
            "risks": ["Transcript input is empty."]
        }

    prompt = PROMPT_TEMPLATE.format(transcript=transcript)

    try:
        response = model.generate_content(prompt)

        raw_output = response.text or ""
        cleaned_output = clean_model_output(raw_output)

        data = json.loads(cleaned_output)
        return apply_fallbacks(data)

    except json.JSONDecodeError:
        return {
            "summary": "Could not parse model output.",
            "decisions": [],
            "tasks": [],
            "risks": ["Gemini response was not valid JSON."]
        }

    except Exception as e:
        return {
            "summary": "API call failed.",
            "decisions": [],
            "tasks": [],
            "risks": [f"Error: {str(e)}"]
        }


if __name__ == "__main__":
    sample_transcript = '''
    We need to finish the hackathon demo by Friday.
    Prarthana will complete the Streamlit UI tonight.
    Nidhi will test the transcription pipeline tomorrow morning.
    Gaurav will prepare the JSON extraction module by tonight.
    We decided not to add database support in the MVP.
    Someone should also prepare sample audio for the demo.
    '''

    result = extract_tasks(sample_transcript)
    print(json.dumps(result, indent=2))