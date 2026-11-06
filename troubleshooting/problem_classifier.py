"""
Classify an instructor's Canvas question or reported problem.

This classifier does not diagnose the issue.
It identifies which troubleshooting path is most relevant.
"""


def classify_problem(problem):
    if not isinstance(problem, str):
        return "unknown"

    text = problem.lower().strip()

    if not text:
        return "unknown"

    # --------------------------------------------------
    # FACTUAL QUESTIONS
    # --------------------------------------------------

    factual_terms = [
        "due date",
        "when is it due",
        "when is this due",
        "is it published",
        "is this published",
        "assignment id",
        "course id",
        "submission method",
        "how do students submit",
        "how can students submit",
        "what can students submit",
    ]

    if any(
        term in text
        for term in factual_terms
    ):
        return "factual"

    # --------------------------------------------------
    # EXTERNAL TOOL / LAB LAUNCH
    # --------------------------------------------------

    external_context_terms = [
        "lab",
        "external tool",
        "lti",
        "dreamscape",
        "external learning tool",
    ]

    launch_problem_terms = [
        "won't open",
        "will not open",
        "cannot open",
        "can't open",
        "unable to open",
        "won't launch",
        "will not launch",
        "cannot launch",
        "can't launch",
        "unable to launch",
        "launch error",
        "blank page",
    ]

    has_external_context = any(
        term in text
        for term in external_context_terms
    )

    has_launch_problem = any(
        term in text
        for term in launch_problem_terms
    )

    if (
        has_external_context
        and has_launch_problem
    ):
        return "external_tool"

    # --------------------------------------------------
    # VISIBILITY
    # --------------------------------------------------

    visibility_terms = [
        "can't see",
        "cannot see",
        "can't find",
        "cannot find",
        "not visible",
        "missing assignment",
        "assignment is missing",
    ]

    if any(
        term in text
        for term in visibility_terms
    ):
        return "visibility"

    # --------------------------------------------------
    # SUBMISSION
    # --------------------------------------------------

    submission_terms = [
        "can't submit",
        "cannot submit",
        "won't submit",
        "will not submit",
        "submission failed",
        "submit button",
        "unable to submit",
    ]

    if any(
        term in text
        for term in submission_terms
    ):
        return "submission"

    # --------------------------------------------------
    # AVAILABILITY / LOCKED
    # --------------------------------------------------

    availability_terms = [
        "locked",
        "not available",
        "unavailable",
        "not open yet",
        "closed",
        "availability",
    ]

    if any(
        term in text
        for term in availability_terms
    ):
        return "availability"

    # --------------------------------------------------
    # GENERAL ACCESS
    # --------------------------------------------------

    access_terms = [
        "can't open",
        "cannot open",
        "can't access",
        "cannot access",
        "unable to open",
        "unable to access",
    ]

    if any(
        term in text
        for term in access_terms
    ):
        return "access"

    return "unknown"