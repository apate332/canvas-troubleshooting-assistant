from datetime import datetime


def make_finding(
    issue,
    severity,
    recommendation,
    category,
    confidence,
    evidence=None,
    required_data=None
):
    """
    Create a consistent troubleshooting finding.
    """

    return {
        "issue": issue,
        "severity": severity,
        "recommendation": recommendation,
        "category": category,
        "confidence": confidence,
        "evidence": evidence or [],
        "required_data": required_data or []
    }


def check_assignment_published(assignment):
    """
    Check whether the assignment is explicitly unpublished.
    """

    findings = []

    published = assignment.get("published")
    workflow_state = assignment.get("workflow_state")

    if published is False:

        findings.append(
            make_finding(
                issue="Assignment is unpublished",
                severity="Warning",
                category="Availability",
                confidence="High",
                evidence=[
                    "published = false"
                ],
                recommendation=(
                    "Publish the assignment if students are expected "
                    "to access it."
                )
            )
        )

    elif published is None and workflow_state is None:

        findings.append(
            make_finding(
                issue="Assignment publishing status could not be verified",
                severity="Information",
                category="Data completeness",
                confidence="Needs more data",
                evidence=[],
                recommendation=(
                    "Provide assignment data containing the publishing "
                    "status before ruling out a visibility problem."
                ),
                required_data=[
                    "published or workflow_state"
                ]
            )
        )

    return findings


def check_due_date(assignment):
    """
    Review due-date information.

    A missing due date is not automatically considered a problem.
    """

    findings = []

    # No due date can be a valid Canvas configuration.
    # Do not create a finding solely because due_at is null.

    return findings


def check_assignment_dates(assignment):
    """
    Check for contradictory assignment availability dates.
    """

    findings = []

    unlock_at = assignment.get("unlock_at")
    lock_at = assignment.get("lock_at")
    due_at = assignment.get("due_at")

    try:

        unlock_date = (
            datetime.fromisoformat(
                unlock_at.replace("Z", "+00:00")
            )
            if unlock_at
            else None
        )

        lock_date = (
            datetime.fromisoformat(
                lock_at.replace("Z", "+00:00")
            )
            if lock_at
            else None
        )

        due_date = (
            datetime.fromisoformat(
                due_at.replace("Z", "+00:00")
            )
            if due_at
            else None
        )

    except (ValueError, TypeError, AttributeError):

        findings.append(
            make_finding(
                issue="Assignment date information could not be interpreted",
                severity="Review",
                category="Availability",
                confidence="Needs more data",
                evidence=[],
                recommendation=(
                    "Verify the assignment due, unlock, and lock "
                    "date values."
                )
            )
        )

        return findings

    if unlock_date and lock_date and unlock_date >= lock_date:

        findings.append(
            make_finding(
                issue="Assignment availability dates are inconsistent",
                severity="Warning",
                category="Availability",
                confidence="High",
                evidence=[
                    f"unlock_at = {unlock_at}",
                    f"lock_at = {lock_at}"
                ],
                recommendation=(
                    "Update the assignment availability window so the "
                    "unlock date occurs before the lock date."
                )
            )
        )

    if due_date and unlock_date and due_date < unlock_date:

        findings.append(
            make_finding(
                issue="Assignment is due before it becomes available",
                severity="Warning",
                category="Availability",
                confidence="High",
                evidence=[
                    f"due_at = {due_at}",
                    f"unlock_at = {unlock_at}"
                ],
                recommendation=(
                    "Review the due date and unlock date. Students "
                    "cannot reasonably complete the assignment before "
                    "it becomes available."
                )
            )
        )

    return findings


def check_submission_type(assignment):
    """
    Review assignment submission configuration.
    """

    findings = []

    submission_types = assignment.get("submission_types")

    if submission_types is None:

        findings.append(
            make_finding(
                issue="Submission configuration could not be verified",
                severity="Information",
                category="Submission",
                confidence="Needs more data",
                evidence=[],
                recommendation=(
                    "Provide assignment data containing submission_types "
                    "before ruling out a submission configuration issue."
                ),
                required_data=[
                    "submission_types"
                ]
            )
        )

        return findings

    if not submission_types:

        findings.append(
            make_finding(
                issue="Assignment has no configured submission type",
                severity="Warning",
                category="Submission",
                confidence="High",
                evidence=[
                    "submission_types is empty"
                ],
                recommendation=(
                    "Review the assignment submission settings and "
                    "configure the intended submission method."
                )
            )
        )

    return findings


def check_external_tool(assignment):
    """
    Identify assignments that require external-tool/LTI investigation.
    """

    findings = []

    submission_types = assignment.get("submission_types") or []

    if "external_tool" not in submission_types:
        return findings

    external_tool = assignment.get("external_tool")

    evidence = [
        "submission_types includes external_tool"
    ]

    if isinstance(external_tool, dict):

        content_type = external_tool.get("content_type")
        content_id = external_tool.get("content_id")
        resource_link_id = external_tool.get("resource_link_id")

        if content_type:
            evidence.append(
                f"content_type = {content_type}"
            )

        if content_id:
            evidence.append(
                f"content_id = {content_id}"
            )

        if resource_link_id:
            evidence.append(
                "resource_link_id is present"
            )

    if isinstance(external_tool, dict) and external_tool:

        findings.append(
            make_finding(
                issue="Assignment uses an external tool",
                severity="Information",
                category="LTI / External Tool",
                confidence="Needs more data",
                evidence=evidence,
                recommendation=(
                    "The assignment is configured to launch through an "
                    "external tool. If students cannot open it, verify "
                    "the LTI tool configuration and resource link. "
                    "Also verify module and course visibility before "
                    "concluding that the external tool is the cause."
                ),
                required_data=[
                    "LTI tool configuration",
                    "module visibility",
                    "course availability"
                ]
            )
        )

    else:

        findings.append(
            make_finding(
                issue="External-tool assignment is missing tool details",
                severity="Review",
                category="LTI / External Tool",
                confidence="Medium",
                evidence=evidence,
                recommendation=(
                    "Retrieve the assignment's external-tool "
                    "configuration before troubleshooting the LTI launch."
                ),
                required_data=[
                    "external_tool_tag_attributes"
                ]
            )
        )

    return findings