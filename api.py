from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any

from troubleshooting.run_checks import (
    run_checks_on_extracted_data
)


app = FastAPI(
    title="Canvas Troubleshooting API"
)


# --------------------------------------------------
# DEVELOPMENT CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
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
        "status": "ok"
    }


# --------------------------------------------------
# TROUBLESHOOT
# --------------------------------------------------

@app.post("/troubleshoot")
def troubleshoot(
    request: TroubleshootingRequest
):
    extracted_data = {
        "assignment": request.assignment
    }

    findings = run_checks_on_extracted_data(
        extracted_data
    )

    return {
        "reported_problem": request.problem,
        "assignment": {
            "assignment_id": (
                request.assignment.get(
                    "assignment_id"
                )
            ),
            "course_id": (
                request.assignment.get(
                    "course_id"
                )
            ),
            "name": (
                request.assignment.get(
                    "name"
                )
            )
        },
        "findings": findings
    }