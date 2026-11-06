from troubleshooting.assignment_checks import (
    check_assignment_published,
    check_due_date,
    check_assignment_dates,
    check_submission_type
)

from troubleshooting.module_checks import (
    check_module_published,
    check_module_items
)

from troubleshooting.module_checks import (
    check_assignment_module_context,
)

from troubleshooting.lti_checks import check_lti_configuration

def run_all_checks(assignment, modules=None):

    all_findings = []

    # Assignment checks
    all_findings.extend(
        check_assignment_published(assignment)
    )

    all_findings.extend(
        check_due_date(assignment)
    )

    all_findings.extend(
        check_assignment_dates(assignment)
    )

    all_findings.extend(
        check_submission_type(assignment)
    )

    all_findings.extend(
        check_assignment_module_context(
            assignment
        )
    )

    # Module checks
    if modules:
        for module in modules:

            all_findings.extend(
                check_module_published(module)
            )

            all_findings.extend(
                check_module_items(module)
            )

    # LTI checks
    all_findings.extend(
        check_lti_configuration(assignment)
    )

    return all_findings


def run_checks_on_extracted_data(extracted_data):
    """
    Run troubleshooting checks based on the
    Canvas response data available.
    """

    all_findings = []

    if not isinstance(extracted_data, dict):
        return all_findings

    # Assignment checks
    assignment = extracted_data.get("assignment")

    if isinstance(assignment, dict):
        all_findings.extend(check_assignment_published(assignment))
        all_findings.extend(check_due_date(assignment))
        all_findings.extend(check_assignment_dates(assignment))
        all_findings.extend(check_submission_type(assignment))
        all_findings.extend(check_lti_configuration(assignment))

    # Module checks
    modules = extracted_data.get("modules", [])

    if isinstance(modules, list):
        for module in modules:
            if not isinstance(module, dict):
                continue

            all_findings.extend(check_module_published(module))
            all_findings.extend(check_module_items(module))

    return all_findings