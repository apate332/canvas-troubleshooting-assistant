from extraction.extract_json import process_assignment

from troubleshooting.assignment_checks import (
    check_assignment_published,
    check_due_date,
    check_assignment_dates,
    check_submission_type
)

from database.connection import get_connection

from database.operations import save_assignment

from database.operations import save_findings

from database.operations import get_findings

from troubleshooting.module_checks import (
    check_module_published,
    check_module_items
)

from troubleshooting.lti_checks import check_lti_configuration

from troubleshooting.run_checks import run_all_checks

from reports.report_generator import generate_report

from reports.report_generator import generate_report, save_report

file_path = "data/sample_assignment.json"

assignment, errors = process_assignment(file_path)

print("\nEXTRACTED ASSIGNMENT INFORMATION")

for field, value in assignment.items():
    print(f"{field}: {value}")


print("\nVALIDATION RESULTS")

if errors:
    for error in errors:
        print(error)
else:
    print("Assignment information is valid.")

print("\nDUE DATE CHECK")

all_findings = []

all_findings.extend(check_assignment_published(assignment))
all_findings.extend(check_due_date(assignment))
all_findings.extend(check_assignment_dates(assignment))
all_findings.extend(check_submission_type(assignment))

due_date_findings = check_due_date(assignment)

if due_date_findings:
    for finding in due_date_findings:
        print("Issue:", finding["issue"])
        print("Severity:", finding["severity"])
        print("Recommendation:", finding["recommendation"])
else:
    print("Due date is available.")

from database.connection import get_connection

try:
    connection = get_connection()

    print("Successfully connected to PostgreSQL!")

    connection.close()

    print("Database connection closed.")

except Exception as error:
    print("Database connection failed:")
    print(error)

print("\nSAVING ASSIGNMENT TO DATABASE")

save_assignment(assignment)

print("\nSAVING TROUBLESHOOTING FINDINGS")

save_findings(
    assignment["assignment_id"],
    all_findings
)

print("\nRETRIEVING SAVED FINDINGS")

saved_findings = get_findings(assignment["assignment_id"])

for finding in saved_findings:
    print("Issue:", finding["issue"])
    print("Severity:", finding["severity"])
    print("Recommendation:", finding["recommendation"])

sample_module = {
    "name": "Week 1: Introduction",
    "published": True,
    "items": [
        {
            "title": "Introduction Page",
            "published": True
        },
        {
            "title": "Week 1 Assignment",
            "published": False
        }
    ]
}

print("\nMODULE TROUBLESHOOTING RESULTS")

module_findings = []

module_findings.extend(
    check_module_published(sample_module)
)

module_findings.extend(
    check_module_items(sample_module)
)

if module_findings:
    for finding in module_findings:
        print("Issue:", finding["issue"])
        print("Severity:", finding["severity"])
        print("Recommendation:", finding["recommendation"])
else:
    print("No module issues found.")

sample_lti_assignment = {
    "assignment_id": 789,
    "name": "External Tool Assignment",
    "submission_types": ["external_tool"],
    "external_tool_url": None
}

print("\nLTI TROUBLESHOOTING RESULTS")

lti_findings = check_lti_configuration(sample_lti_assignment)

if lti_findings:
    for finding in lti_findings:
        print("Issue:", finding["issue"])
        print("Severity:", finding["severity"])
        print("Recommendation:", finding["recommendation"])
else:
    print("No LTI configuration issues found.")

print("\nCOMPLETE TROUBLESHOOTING RESULTS")

all_findings = run_all_checks(
    assignment,
    [sample_module]
)

print("\nGENERATING TROUBLESHOOTING REPORT")

report = generate_report(
    assignment,
    all_findings
)

print(report)

if all_findings:

    for finding in all_findings:
        print("\nIssue:", finding["issue"])
        print("Severity:", finding["severity"])
        print("Recommendation:", finding["recommendation"])

else:
    print("No troubleshooting issues found.")

save_report(
    report,
    "reports/canvas_troubleshooting_report.txt"
)