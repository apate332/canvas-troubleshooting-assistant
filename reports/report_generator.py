from datetime import datetime


def generate_report(assignment, findings):

    report = []

    report.append("=" * 50)
    report.append("CANVAS TROUBLESHOOTING REPORT")
    report.append("=" * 50)

    report.append(f"Assignment: {assignment['name']}")
    report.append(f"Assignment ID: {assignment['assignment_id']}")
    report.append(f"Course ID: {assignment['course_id']}")

    report.append(
        f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    report.append("-" * 50)

    report.append(f"Total Issues Found: {len(findings)}")

    report.append("-" * 50)

    if findings:

        for number, finding in enumerate(findings, start=1):

            report.append(f"\nIssue {number}")
            report.append(f"Issue: {finding['issue']}")
            report.append(f"Severity: {finding['severity']}")
            report.append(
                f"Recommendation: {finding['recommendation']}"
            )

    else:
        report.append("No troubleshooting issues were identified.")

    report.append("\n" + "=" * 50)
    report.append("END OF REPORT")
    report.append("=" * 50)

    return "\n".join(report)

def save_report(report, file_path):

    with open(file_path, "w", encoding="utf-8") as file:

        file.write(report)

    print(f"Report successfully saved to: {file_path}")