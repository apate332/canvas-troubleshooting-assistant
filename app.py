import html
import io
import json

import streamlit as st

from extraction.extract_json import process_json
from troubleshooting.run_checks import run_checks_on_extracted_data
from reports.report_generator import generate_report
from database.operations import (
    save_assignment,
    save_findings,
    get_findings,
    get_troubleshooting_history,
)
from database.connection import is_database_enabled

database_enabled = is_database_enabled()

st.set_page_config(
    page_title="Canvas Troubleshooting Assistant",
    layout="wide",
)


st.markdown(
    """
    <style>
    .stApp { background: #f6f7fb; }
    .block-container {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }
    h1 { color: #171a2b; letter-spacing: -0.035em; }
    h2, h3 { color: #22263a; letter-spacing: -0.02em; }
    div[data-testid="stRadio"] > div { gap: 0.5rem; }
    div[data-testid="stTextArea"] textarea {
        border-radius: 14px;
        border: 1px solid #dfe3ee;
        background: #ffffff;
    }
    .stButton > button, .stDownloadButton > button {
        border-radius: 10px;
        min-height: 44px;
        font-weight: 650;
    }
    [data-testid="stDataFrame"] {
        background: #ffffff;
        border: 1px solid #e4e7ef;
        border-radius: 16px;
        overflow: hidden;
    }
    [data-testid="stAlert"] { border-radius: 12px; }
    .section-kicker {
        color: #777c91;
        font-size: 0.76rem;
        font-weight: 750;
        letter-spacing: 0.11em;
        text-transform: uppercase;
        margin: 1.8rem 0 0.35rem 0;
    }
    .metric-card {
        background: #ffffff;
        border: 1px solid #e5e7ef;
        border-radius: 16px;
        padding: 18px 20px;
        min-height: 105px;
        box-shadow: 0 4px 18px rgba(24, 29, 55, 0.04);
    }
    .metric-label {
        color: #85899a;
        font-size: 0.72rem;
        font-weight: 750;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .metric-value {
        color: #202438;
        font-size: 1.18rem;
        font-weight: 720;
        line-height: 1.25;
        overflow-wrap: anywhere;
    }
    .status-dot {
        display: inline-block;
        width: 9px;
        height: 9px;
        border-radius: 50%;
        background: #22a06b;
        margin-right: 7px;
    }
    .diagnostic-card {
        background: #ffffff;
        border: 1px solid #e1e5ee;
        border-radius: 18px;
        padding: 24px 26px;
        margin: 0.8rem 0 1rem 0;
        box-shadow: 0 5px 22px rgba(24, 29, 55, 0.05);
    }
    .diag-top {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        align-items: center;
        margin-bottom: 14px;
        flex-wrap: wrap;
    }
    .diag-category {
        color: #575d76;
        font-size: 0.75rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .diag-badge {
        background: #fff4d6;
        color: #765500;
        border: 1px solid #f4d77e;
        padding: 5px 10px;
        border-radius: 999px;
        font-size: 0.76rem;
        font-weight: 750;
    }
    .diag-title {
        color: #1c2033;
        font-size: 1.18rem;
        font-weight: 760;
        margin-bottom: 10px;
    }
    .diag-copy {
        color: #4e5368;
        line-height: 1.65;
        margin-bottom: 18px;
    }
    .diag-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 22px;
        margin: 16px 0 18px 0;
    }
    .diag-heading {
        color: #2e3348;
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 0.07em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .diag-list {
        color: #51566b;
        line-height: 1.7;
        font-size: 0.92rem;
    }
    .recommendation-box {
        background: #f5f6ff;
        border-left: 4px solid #5b5bd6;
        border-radius: 8px;
        padding: 14px 16px;
        color: #383d56;
        line-height: 1.6;
    }
    .recognition-line {
        color: #6c7185;
        font-size: 0.86rem;
        margin-top: 0.25rem;
    }
    @media (max-width: 800px) {
        .diag-grid { grid-template-columns: 1fr; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def safe_text(value, fallback="Not available"):
    if value is None or value == "":
        return fallback
    return str(value)


def humanize(value, fallback="Not set"):
    if value is None or value == "":
        return fallback
    return str(value).replace("_", " ").title()


def metric_card(label, value, status=False):
    dot = '<span class="status-dot"></span>' if status else ""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{html.escape(str(label))}</div>
            <div class="metric-value">{dot}{html.escape(str(value))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_diagnostic_card(finding):
    category = finding.get("category") or "Troubleshooting"
    confidence = finding.get("confidence") or finding.get("severity") or "Review"
    issue = finding.get("issue") or "Troubleshooting finding"
    recommendation = finding.get("recommendation") or "No recommendation available."
    evidence = finding.get("evidence") or []
    required_data = finding.get("required_data") or []

    evidence_html = "".join(
        f"<div>✓ {html.escape(str(item))}</div>" for item in evidence
    ) or "<div>No supporting evidence was recorded.</div>"

    required_html = "".join(
        f"<div>? {html.escape(str(item))}</div>" for item in required_data
    ) or "<div>No additional data is currently required.</div>"

    st.markdown(
        f"""
        <div class="diagnostic-card">
            <div class="diag-top">
                <div class="diag-category">{html.escape(str(category))}</div>
                <div class="diag-badge">{html.escape(str(confidence))}</div>
            </div>
            <div class="diag-title">{html.escape(str(issue))}</div>
            <div class="diag-grid">
                <div>
                    <div class="diag-heading">Evidence</div>
                    <div class="diag-list">{evidence_html}</div>
                </div>
                <div>
                    <div class="diag-heading">Additional data needed</div>
                    <div class="diag-list">{required_html}</div>
                </div>
            </div>
            <div class="diag-heading">Recommended next step</div>
            <div class="recommendation-box">{html.escape(str(recommendation))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.title("Canvas Troubleshooting Assistant")

st.markdown('<div class="section-kicker">Canvas data input</div>', unsafe_allow_html=True)
st.subheader("Provide Canvas Data")

input_method = st.radio(
    "How would you like to provide your Canvas data?",
    ["Paste JSON", "Upload JSON"],
    horizontal=True,
)

pasted_json = ""
uploaded_files = []

if input_method == "Paste JSON":
    pasted_json = st.text_area(
        "Paste your Canvas JSON response here",
        height=280,
        placeholder='{\n    "id": 12345,\n    "due_at": null,\n    "graded": true\n}',
    )
    st.caption(
        f"Captured: {len(pasted_json):,} characters "
        f"({len(pasted_json.encode('utf-8')):,} bytes)"
    )
else:
    uploaded_files = st.file_uploader(
        "Upload one or more Canvas JSON files",
        type=["json"],
        accept_multiple_files=True,
    )
    if uploaded_files:
        st.success(f"{len(uploaded_files)} file(s) uploaded.")

if input_method == "Paste JSON":
    input_sources = (
        [("Pasted JSON", io.StringIO(pasted_json))]
        if pasted_json.strip()
        else []
    )
else:
    input_sources = (
        [(uploaded_file.name, uploaded_file) for uploaded_file in uploaded_files]
        if uploaded_files
        else []
    )

if input_sources and st.button("Start Troubleshooting", type="primary"):
    combined_data = {}
    recognized_by_file = {}
    processing_errors = []

    for source_name, source in input_sources:
        try:
            data, recognized_types, extracted = process_json(source)
            recognized_by_file[source_name] = recognized_types

            for data_type, value in extracted.items():
                if data_type == "modules":
                    combined_data.setdefault("modules", [])
                    combined_data["modules"].extend(value)
                elif data_type == "navigation":
                    combined_data.setdefault(
                        "navigation",
                        {"items": [], "modules": []},
                    )
                    combined_data["navigation"]["items"].extend(
                        value.get("items", [])
                    )
                    combined_data["navigation"]["modules"].extend(
                        value.get("modules", [])
                    )
                elif data_type == "assignment":
                    combined_data["assignment"] = value
                else:
                    combined_data[data_type] = value

        except json.JSONDecodeError:
            processing_errors.append(f"{source_name}: Invalid JSON.")
        except Exception as error:
            processing_errors.append(f"{source_name}: {error}")

    for error in processing_errors:
        st.warning(error)

    if not recognized_by_file:
        st.error("No JSON input could be processed.")
        st.stop()

    if all(types == ["unknown"] for types in recognized_by_file.values()):
        st.warning(
            "The JSON was readable, but no supported Canvas response type "
            "was recognized."
        )
        st.stop()

    assignment = combined_data.get("assignment")

    try:
        findings = run_checks_on_extracted_data(combined_data)
    except Exception as error:
        st.error(f"Troubleshooting checks failed: {error}")
        st.stop()

    workflow_state = None
    status = "Unknown"
    submission_display = "Not set"
    attempts_display = "Not set"

    if isinstance(assignment, dict):
        workflow_state = assignment.get("workflow_state")
        if workflow_state:
            status = humanize(workflow_state, "Unknown")
        elif assignment.get("published") is True:
            status = "Published"
        elif assignment.get("published") is False:
            status = "Unpublished"

        submission_types = assignment.get("submission_types")
        if submission_types:
            submission_display = ", ".join(
                humanize(value, "") for value in submission_types
            )

        allowed_attempts = assignment.get("allowed_attempts")
        if allowed_attempts == -1:
            attempts_display = "Unlimited"
        elif allowed_attempts is not None:
            attempts_display = str(allowed_attempts)

    confidence_values = [
        finding.get("confidence")
        for finding in findings
        if finding.get("confidence")
    ]
    if not findings:
        confidence_display = "No issues detected"
    elif any(value == "Needs more data" for value in confidence_values):
        confidence_display = "Needs more data"
    elif confidence_values:
        confidence_display = confidence_values[0]
    else:
        confidence_display = "Review"

    st.markdown(
        '<div class="section-kicker">Current analysis</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Troubleshooting Overview")

    overview = st.columns(6)
    with overview[0]:
        metric_card(
            "Course",
            assignment.get("course_id", "Not available")
            if isinstance(assignment, dict)
            else "Not available",
        )
    with overview[1]:
        metric_card(
            "Assignment",
            assignment.get("assignment_id", "Not available")
            if isinstance(assignment, dict)
            else "Not available",
        )
    with overview[2]:
        metric_card("Status", status, status == "Published")
    with overview[3]:
        metric_card("Issues found", len(findings))
    with overview[4]:
        metric_card("Submission", submission_display)
    with overview[5]:
        metric_card("Confidence", confidence_display)

    recognized_summary = " | ".join(
        f"{name}: {', '.join(types)}"
        for name, types in recognized_by_file.items()
    )
    st.markdown(
        f'<div class="recognition-line">Recognized: '
        f'{html.escape(recognized_summary)}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-kicker">Configuration</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Assignment Configuration")

    if isinstance(assignment, dict):
        assignment_table = [
            {
                "Course ID": safe_text(assignment.get("course_id")),
                "Assignment ID": safe_text(assignment.get("assignment_id")),
                "Assignment Group ID": safe_text(
                    assignment.get("assignment_group_id")
                ),
                "Assignment Name": safe_text(assignment.get("name")),
                "Status": status,
                "Due Date": safe_text(assignment.get("due_at"), "Not set"),
                "Unlock Date": safe_text(
                    assignment.get("unlock_at"), "Not set"
                ),
                "Lock Date": safe_text(assignment.get("lock_at"), "Not set"),
                "Submission Type": submission_display,
                "Points": safe_text(
                    assignment.get("points_possible"), "Not set"
                ),
                "Grading Type": humanize(
                    assignment.get("grading_type"), "Not set"
                ),
                "Attempts": attempts_display,
            }
        ]
        st.dataframe(
            assignment_table,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No assignment information was found in this input.")

    st.markdown(
        '<div class="section-kicker">Diagnosis</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Diagnostic Results")

    if findings:
        for finding in findings:
            render_diagnostic_card(finding)
    else:
        st.success("No issues were identified by the available checks.")

    saved_findings = findings
    run_id = None


    can_save_assignment = (
        isinstance(assignment, dict)
        and assignment.get("assignment_id") is not None
        and assignment.get("course_id") is not None
        and bool(assignment.get("name"))
        and assignment.get("published") is not None
    )

    if can_save_assignment and database_enabled:

        try:
            save_assignment(assignment)

            run_id = save_findings(
                assignment["assignment_id"],
                findings
            )

            saved_findings = get_findings(run_id)

        except Exception as error:
            st.warning(
                "The troubleshooting analysis completed successfully, "
                "but the result could not be saved."
            )
    elif can_save_assignment and not database_enabled:
            # Stateless mode.
            # The troubleshooting result remains available for
            # display and report generation without being saved.
            run_id = None

    elif assignment is not None:
        st.info(
            "Assignment data was recognized, but it is missing fields "
            "required by the current database. Results are displayed "
            "but were not saved."
        )
    else:
        st.info(
            "No assignment was available. Module, navigation, and "
            "configuration results are displayed without creating an "
            "assignment database record."
        )

    if isinstance(assignment, dict):
        report_assignment = {
            "name": assignment.get("name") or "Unavailable",
            "assignment_id": assignment.get("assignment_id") or "Unavailable",
            "course_id": assignment.get("course_id") or "Unavailable",
        }
    else:
        report_assignment = {
            "name": "Not available",
            "assignment_id": "Not available",
            "course_id": "Not available",
        }

    report = generate_report(report_assignment, saved_findings)
    report += "\n\nRECOGNIZED RESPONSE TYPES\n"
    for filename, types in recognized_by_file.items():
        report += f"\n{filename}: {', '.join(types)}"

    st.markdown(
        '<div class="section-kicker">Report</div>',
        unsafe_allow_html=True,
    )
    download_col, _ = st.columns([1, 3])
    with download_col:
        st.download_button(
            label="Download Troubleshooting Report",
            data=report,
            file_name="canvas_troubleshooting_report.txt",
            mime="text/plain",
            use_container_width=True,
        )

    if database_enabled and run_id is not None:
        with st.expander("Previous troubleshooting runs"):
            try:
                history = get_troubleshooting_history(
                    assignment["assignment_id"]
                )
                if history:
                    history_rows = []
                    for run in history:
                        previous_findings = get_findings(run["run_id"])
                        history_rows.append(
                            {
                                "Run": run["run_id"],
                                "Created": run["created_at"],
                                "Findings": len(previous_findings),
                                "Warnings": sum(
                                    1
                                    for finding in previous_findings
                                    if finding["severity"] == "Warning"
                                ),
                                "Review": sum(
                                    1
                                    for finding in previous_findings
                                    if finding["severity"] == "Review"
                                ),
                            }
                        )
                    st.dataframe(
                        history_rows,
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info("No troubleshooting history is available.")
            except Exception as error:
                st.warning(
                    f"Could not retrieve troubleshooting history: {error}"
                )
