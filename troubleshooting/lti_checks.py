
def check_lti_configuration(assignment):

    findings = []

    if not isinstance(assignment, dict):
        return findings

    submission_types = assignment.get("submission_types")

    # No submission type information means we cannot evaluate LTI.
    if not isinstance(submission_types, list):
        return findings

    # Only evaluate assignments that use an external tool.
    if "external_tool" not in submission_types:
        return findings

    # The current assignment response does not provide enough
    # verified information to determine whether LTI is configured.
    findings.append({
        "issue": "External tool submission detected",
        "severity": "Information",
        "recommendation": (
            "This assignment uses an external tool. "
            "Upload the relevant Canvas external tool or LTI "
            "configuration response to investigate its setup."
        )
    })

    return findings
