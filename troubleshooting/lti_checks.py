def check_lti_configuration(assignment):
    """
    Check whether there is a confirmed external-tool problem.

    Using an external tool is not itself an issue.
    A finding should only be returned when there is
    evidence of an actual configuration problem.
    """

    findings = []

    if not isinstance(assignment, dict):
        return findings

    submission_types = assignment.get(
        "submission_types"
    )

    if not isinstance(submission_types, list):
        return findings

    # This is not an external-tool assignment.
    if "external_tool" not in submission_types:
        return findings

    # External tool usage by itself is informational
    # context, not a troubleshooting problem.
    #
    # Future checks can be added here when the
    # extension provides verified evidence such as:
    #
    # - missing external-tool URL
    # - missing resource link
    # - failed launch request
    # - HTTP/network failure
    # - LTI launch error
    #
    # Until then, do not invent an LTI problem.

    return findings