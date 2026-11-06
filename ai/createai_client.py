import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from dotenv import load_dotenv


load_dotenv()


CREATEAI_URL = "https://api-main.aiml.asu.edu/query"


def get_createai_key():
    api_key = os.getenv("CREATEAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "CREATEAI_API_KEY is not configured."
        )

    return api_key


def format_arizona_datetime(value):
    """
    Convert a Canvas ISO timestamp into a clear
    Arizona date/time for instructor-facing responses.
    """

    if not value:
        return "None"

    try:
        parsed = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )

        arizona_time = parsed.astimezone(
            ZoneInfo("America/Phoenix")
        )

        return arizona_time.strftime(
            "%B %-d, %Y at %-I:%M %p Arizona Time (MST)"
        )

    except (ValueError, TypeError):
        return str(value)


def format_submission_types(submission_types):
    if not isinstance(submission_types, list):
        return "Not specified"

    labels = {
        "online_upload": "Upload a File",
        "online_text_entry": "Text Entry",
        "online_url": "Website URL",
        "media_recording": "Media Recording",
        "student_annotation": "Student Annotation",
        "external_tool": "External Learning Tool",
        "none": "No Online Submission",
        "on_paper": "In-Person Submission"
    }

    return " · ".join(
        labels.get(value, value)
        for value in submission_types
    )


def build_canvas_context(assignment):
    submission_types = assignment.get(
        "submission_types",
        []
    )

    uses_external_tool = (
        isinstance(submission_types, list)
        and "external_tool" in submission_types
    )

    external_tool_details = assignment.get(
        "external_tool"
    )

    module_context = assignment.get(
    "module_context"
    )

    if not isinstance(module_context, dict):
        module_context = {}

    return {
        "assignment_name":
            assignment.get("name"),

        "assignment_id":
            assignment.get("assignment_id"),

        "course_id":
            assignment.get("course_id"),

        "published":
            assignment.get("published"),

        "submission_methods":
            format_submission_types(
                submission_types
            ),

        "due_date":
            format_arizona_datetime(
                assignment.get("due_at")
            ),

        "unlock_date":
            format_arizona_datetime(
                assignment.get("unlock_at")
            ),

        "lock_date":
            format_arizona_datetime(
                assignment.get("lock_at")
            ),

        "uses_external_tool":
            uses_external_tool,

        "external_tool_details_available":
            bool(external_tool_details),

        "workflow_state":
            assignment.get("workflow_state"),

        "allowed_attempts":
            assignment.get("allowed_attempts"),

        "points_possible":
            assignment.get("points_possible"),

        "grading_type":
            assignment.get("grading_type"),

        "module_context_available":
            bool(module_context),

        "module_name":
            module_context.get(
                "module_name"
            ),

        "module_published":
            module_context.get(
                "module_published"
            ),

        "module_item_published":
            module_context.get(
                "module_item_published"
            ),

        "module_item_title":
           module_context.get(
                "module_item_title"
            ),

        "require_sequential_progress":
            module_context.get(
                "require_sequential_progress"
            ),

        "module_unlock_at":
            format_arizona_datetime(
                module_context.get(
                    "module_unlock_at"
                )
            )
   
    if module_context
    else "Not verified",
    }


def explain_diagnosis(
    reported_problem,
    problem_type,
    findings,
    assignment
):
    api_key = get_createai_key()

    canvas_context = build_canvas_context(
        assignment
    )

    findings_text = []

    for finding in findings:
        findings_text.append(
            {
                "issue":
                    finding.get("issue"),

                "severity":
                    finding.get("severity"),

                "recommendation":
                    finding.get("recommendation")
            }
        )

    query = f"""
You are assisting an instructor or course designer
who is troubleshooting the Canvas activity they are
currently viewing.

USER QUESTION OR REPORTED PROBLEM:

{reported_problem}

PROBLEM TYPE:

{problem_type}

VERIFIED CANVAS INFORMATION:

MODULE CONTEXT:

Module context available:
{canvas_context["module_context_available"]}

Module name:
{canvas_context["module_name"]}

Module published:
{canvas_context["module_published"]}

Module item published:
{canvas_context["module_item_published"]}

Module item title:
{canvas_context["module_item_title"]}

Sequential progression required:
{canvas_context["require_sequential_progress"]}

Module unlock date:
{canvas_context["module_unlock_at"]}

Assignment name:
{canvas_context["assignment_name"]}

Assignment ID:
{canvas_context["assignment_id"]}

Course ID:
{canvas_context["course_id"]}

Published:
{canvas_context["published"]}

Submission methods:
{canvas_context["submission_methods"]}

Due date:
{canvas_context["due_date"]}

Unlock restriction:
{canvas_context["unlock_date"]}

Lock restriction:
{canvas_context["lock_date"]}

Uses an external learning tool:
{canvas_context["uses_external_tool"]}

External-tool details available:
{canvas_context["external_tool_details_available"]}

Workflow state:
{canvas_context["workflow_state"]}

Allowed attempts:
{canvas_context["allowed_attempts"]}

Points possible:
{canvas_context["points_possible"]}

Grading type:
{canvas_context["grading_type"]}


DETERMINISTIC TROUBLESHOOTING FINDINGS:

{findings_text}


INSTRUCTIONS:

Use only the verified Canvas information and deterministic
findings supplied above.

Determine what kind of response the user needs.

Use one of these response types:

- "fact" for simple questions about the assignment, such as
  due date, publication status, submission method, assignment
  name, assignment ID, or course ID.

- "instruction" when the user asks how to perform something.

- "confirmed_issue" when the evidence identifies a confirmed
  Canvas configuration problem.

- "next_steps" when the user reports a problem but the
  available evidence does not confirm the cause.

Always answer the user's actual question.

A confirmed deterministic finding takes priority over
speculative causes.

If no confirmed cause exists, provide the most useful
preliminary troubleshooting step instead of simply saying
that no issue was found.

Prioritize information that is directly relevant to the
user's reported problem.

Do not include every verified Canvas fact in the main answer.
Use the "verified" field for supporting evidence when useful.

Only mention the assignment due date when:
- the user asks about the due date,
- the due date is directly relevant to the reported problem, or
- the due date materially affects the recommended next step.

Do not present a past due date as an access restriction.
A due date alone does not mean an assignment is locked or
unavailable.

Never claim an external learning tool is broken merely
because the assignment uses one.

Never invent Canvas settings.

Never ask the instructor to inspect developer tools,
network traffic, JSON, or API responses.

Use the supplied human-readable Arizona date/time when
mentioning dates.

Return ONLY valid JSON.

Do not use Markdown.
Do not wrap the JSON in a code block.
Do not include any text before or after the JSON.

Use exactly this structure:

{{
    "response_type": "fact | instruction | confirmed_issue | next_steps",
    "headline": "Short, clear headline",
    "answer": "Concise explanation answering the user's question",
    "steps": [],
    "verified": [],
    "important": null
}}

Rules for fields:

"headline":
Keep this short and instructor-friendly.

"answer":
Use 1-3 concise sentences.

"steps":
Use an empty list unless useful actions or instructions
are needed.

"verified":
Include only facts directly supported by the supplied
Canvas information or deterministic findings.

"important":
Use null unless there is an important caveat the
instructor should know.
""".strip()

    headers = {
        "Authorization":
            f"Bearer {api_key}",

        "Content-Type":
            "application/json"
    }

    payload = {
        "query": query
    }

    response = requests.post(
        CREATEAI_URL,
        json=payload,
        headers=headers,
        timeout=60
    )

    response.raise_for_status()

    data = response.json()

    raw_answer = data.get("response")

    if not raw_answer:
        raise RuntimeError(
            "CreateAI returned no response text."
        )

    try:
        structured_answer = json.loads(
            raw_answer
        )

    except json.JSONDecodeError:
        structured_answer = {
            "response_type": "fact",
            "headline": "Answer",
            "answer": raw_answer,
            "steps": [],
            "verified": [],
            "important": None
        }

    return {
        "response": structured_answer,
        "metadata": data.get(
            "metadata",
            {}
        )
    }