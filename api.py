import logging
import os
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from ai.createai_client import explain_diagnosis
from troubleshooting.run_checks import (
    run_checks_on_extracted_data,
)
from troubleshooting.problem_classifier import (
    classify_problem,
)

load_dotenv()

# --------------------------------------------------
# LOGGING
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO
)

logger = logging.getLogger(
    "canvas_troubleshooter"
)


# --------------------------------------------------
# APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="Canvas Troubleshooting API",
    version="0.1.0",
)


# --------------------------------------------------
# ENVIRONMENT
# --------------------------------------------------

environment = os.getenv(
    "ENVIRONMENT",
    "development"
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

# Development currently allows browser-extension
# requests from any origin.
#
# Before production deployment, replace this with
# the approved extension/application origins.

allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "*"
)

if allowed_origins == "*":
    cors_origins = ["*"]
else:
    cors_origins = [
        origin.strip()
        for origin in allowed_origins.split(",")
        if origin.strip()
    ]


app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=[
        "GET",
        "POST",
        "OPTIONS",
    ],
    allow_headers=[
        "Content-Type",
    ],
)


# --------------------------------------------------
# REQUEST MODEL
# --------------------------------------------------

class TroubleshootingRequest(BaseModel):
    problem: str
    assignment: dict[str, Any]


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "environment": environment,
    }


# --------------------------------------------------
# TROUBLESHOOT
# --------------------------------------------------

@app.post("/troubleshoot")
def troubleshoot(
    request: TroubleshootingRequest
):
    assignment = request.assignment

    problem_type = classify_problem(
    request.problem
    )

    extracted_data = {
        "assignment": assignment
    }

    # --------------------------------------------------
    # STEP 1
    # Run deterministic troubleshooting checks.
    # --------------------------------------------------

    try:
        findings = run_checks_on_extracted_data(
            extracted_data
        )

    except Exception:
        logger.exception(
            "Deterministic troubleshooting checks failed."
        )

        findings = []


    # --------------------------------------------------
    # STEP 2
    # Ask CreateAI to explain the verified evidence.
    #
    # CreateAI failure must NOT cause the entire
    # troubleshooting request to fail.
    # --------------------------------------------------

    ai_response = None
    ai_available = False

    try:
       ai_response = explain_diagnosis(
            reported_problem=request.problem,
            problem_type=problem_type,
            findings=findings,
            assignment=assignment,
        )

       ai_available = True

    except Exception:
        logger.exception(
            "CreateAI explanation failed."
        )


    # --------------------------------------------------
    # STEP 3
    # Extract only the structured CreateAI response.
    # --------------------------------------------------

    diagnosis = None

    if (
        ai_response
        and isinstance(ai_response, dict)
    ):
        diagnosis = ai_response.get(
            "response"
        )


    # --------------------------------------------------
    # STEP 4
    # Return the application response.
    # --------------------------------------------------

    return {
        "status": "success",

        "problem_type":
            problem_type,

        "reported_problem":
            request.problem,

        "assignment": {
            "assignment_id":
                assignment.get(
                    "assignment_id"
                ),

            "course_id":
                assignment.get(
                    "course_id"
                ),

            "name":
                assignment.get(
                    "name"
                ),
        },

        "findings":
            findings,

        "ai_available":
            ai_available,

        "ai_response": {
            "response": diagnosis
        } if diagnosis else None,
    }