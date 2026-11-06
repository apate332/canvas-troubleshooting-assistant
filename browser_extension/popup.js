// ============================================================
// Canvas Troubleshooting Assistant
// popup.js
// ============================================================

const API_BASE_URL = "http://127.0.0.1:8000";
// ------------------------------------------------------------
// UI ELEMENTS
// ------------------------------------------------------------

const statusElement =
    document.getElementById("status");

const connectionStatus =
    document.getElementById("connectionStatus");

const connectionText =
    document.getElementById("connectionText");

const activityCard =
    document.getElementById("activityCard");

const activityNameElement =
    document.getElementById("activityName");

const pageTypeElement =
    document.getElementById("pageType");

const activityIdElement =
    document.getElementById("activityId");

const courseIdElement =
    document.getElementById("courseId");

const publishStatusElement =
    document.getElementById("publishStatus");

const submissionLabel =
    document.getElementById("submissionLabel");

const submissionTypeElement =
    document.getElementById("submissionType");

const dueDateElement =
    document.getElementById("dueDate");

const dueTimeElement =
    document.getElementById("dueTime");

const unlockDateElement =
    document.getElementById("unlockDate");

const lockDateElement =
    document.getElementById("lockDate");

const externalToolElement =
    document.getElementById("externalTool");

const troubleshootButton =
    document.getElementById("troubleshootButton");

const problemSection =
    document.getElementById("problemSection");

const problemInput =
    document.getElementById("problemInput");

const analyzeButton =
    document.getElementById("analyzeButton");

const resultsSection =
    document.getElementById("resultsSection");

const resultsContent =
    document.getElementById("resultsContent");


// ------------------------------------------------------------
// CURRENT ASSIGNMENT
// ------------------------------------------------------------

let collectedAssignment = null;


// ------------------------------------------------------------
// SUBMISSION METHOD FORMATTING
// ------------------------------------------------------------

function formatSubmissionTypes(submissionTypes) {
    if (
        !Array.isArray(submissionTypes) ||
        submissionTypes.length === 0
    ) {
        return {
            label: "Submission Method",
            value: "Not specified"
        };
    }

    const labels = {
        online_upload: "Upload a File",
        online_text_entry: "Text Entry",
        online_url: "Website URL",
        media_recording: "Media Recording",
        student_annotation: "Student Annotation",
        external_tool: "External Learning Tool",
        none: "No Online Submission",
        on_paper: "In-Person Submission"
    };

    const formatted =
        submissionTypes.map(
            (type) => labels[type] || type
        );

    return {
        label:
            formatted.length > 1
                ? "Submission Methods"
                : "Submission Method",

        value: formatted.join(" · ")
    };
}


// ------------------------------------------------------------
// DATE FORMATTING
// ------------------------------------------------------------

function formatCanvasDate(dateValue) {
    if (!dateValue) {
        return {
            date: "No due date",
            time: ""
        };
    }

    const date = new Date(dateValue);

    if (Number.isNaN(date.getTime())) {
        return {
            date: "Date unavailable",
            time: ""
        };
    }

    const datePart =
        new Intl.DateTimeFormat(
            "en-US",
            {
                timeZone: "America/Phoenix",
                month: "long",
                day: "numeric",
                year: "numeric"
            }
        ).format(date);

    const timePart =
        new Intl.DateTimeFormat(
            "en-US",
            {
                timeZone: "America/Phoenix",
                hour: "numeric",
                minute: "2-digit",
                hour12: true
            }
        ).format(date);

    return {
        date: datePart,
        time: `${timePart} Arizona Time (MST)`
    };
}


// ------------------------------------------------------------
// TECHNICAL DATE
// Used only inside Technical Details.
// ------------------------------------------------------------

function formatTechnicalDate(dateValue) {
    if (!dateValue) {
        return "None";
    }

    const formatted =
        formatCanvasDate(dateValue);

    if (!formatted.time) {
        return formatted.date;
    }

    return `${formatted.date} at ${formatted.time}`;
}


// ------------------------------------------------------------
// ACTIVE TAB
// ------------------------------------------------------------

async function getActiveTab() {
    const tabs =
        await chrome.tabs.query({
            active: true,
            currentWindow: true
        });

    if (!tabs.length) {
        throw new Error(
            "No active browser tab found."
        );
    }

    return tabs[0];
}


// ------------------------------------------------------------
// CONTENT SCRIPT
// ------------------------------------------------------------

async function ensureContentScript(tabId) {
    try {
        const response =
            await chrome.tabs.sendMessage(
                tabId,
                {
                    type: "PING"
                }
            );

        if (
            response &&
            response.ready
        ) {
            return;
        }

    } catch (error) {
        // content.js is not loaded yet.
    }

    await chrome.scripting.executeScript({
        target: {
            tabId: tabId
        },
        files: [
            "content.js"
        ]
    });
}


// ------------------------------------------------------------
// DETECT CURRENT CANVAS PAGE
// ------------------------------------------------------------

async function detectCurrentPage() {
    troubleshootButton.disabled = true;

    statusElement.textContent =
        "Detecting the current activity...";

    try {
        const tab =
            await getActiveTab();

    if (
        !tab.url ||
        tab.url.startsWith("chrome://") ||
        tab.url.startsWith("chrome-extension://")
    ) {
        connectionText.textContent =
            "Open Canvas to begin";

        statusElement.textContent =
            "Open a Canvas course or assignment, then reopen the troubleshooter.";

        troubleshootButton.disabled = true;

        return;
    }

    await ensureContentScript(
        tab.id
    );

        const response =
            await chrome.tabs.sendMessage(
                tab.id,
                {
                    type: "GET_CANVAS_CONTEXT"
                }
            );

        if (
            !response ||
            !response.isCanvasPage
        ) {
            connectionText.textContent =
                "Canvas not detected";

            statusElement.textContent =
                "Open a supported Canvas activity to begin.";

            return;
        }

        connectionStatus.classList.add(
            "connected"
        );

        connectionText.textContent =
            "Connected to Canvas";

        activityNameElement.textContent =
            response.activityName ||
            "Canvas Activity";

        pageTypeElement.textContent =
            response.pageType ||
            "Unknown activity";

        activityIdElement.textContent =
            response.activityId ||
            "Not detected";

        courseIdElement.textContent =
            response.courseId ||
            "Not detected";

        activityCard.style.display =
            "block";

        if (
            response.pageType === "Assignment" &&
            response.courseId &&
            response.activityId
        ) {
            statusElement.textContent =
                "Assignment detected.";

            troubleshootButton.disabled =
                false;

        } else {
            statusElement.textContent =
                "This activity type is not yet supported.";

            troubleshootButton.disabled =
                true;
        }

    } catch (error) {
        console.error(
            "Canvas detection failed:",
            error
        );

        connectionText.textContent =
            "Unable to connect";

        statusElement.textContent =
            "Unable to read this Canvas page.";

        troubleshootButton.disabled =
            true;
    }
}


// ------------------------------------------------------------
// COLLECT ASSIGNMENT CONFIGURATION
// ------------------------------------------------------------

async function collectAssignmentData() {
    troubleshootButton.disabled =
        true;

    troubleshootButton.textContent =
        "Reading Canvas...";

    statusElement.textContent =
        "Collecting assignment configuration...";

    try {
        const tab =
            await getActiveTab();

        await ensureContentScript(
            tab.id
        );

        const response =
            await chrome.tabs.sendMessage(
                tab.id,
                {
                    type:
                        "GET_ASSIGNMENT_DATA"
                }
            );

        if (
            !response ||
            response.success !== true
        ) {
            throw new Error(
                response?.error ||
                "Assignment data could not be collected."
            );
        }

        const assignment =
            response.assignment;

        collectedAssignment =
            assignment;


        // ----------------------------------------------------
        // ASSIGNMENT NAME
        // ----------------------------------------------------

        activityNameElement.textContent =
            assignment.name ||
            activityNameElement.textContent;


        // ----------------------------------------------------
        // ASSIGNMENT ID
        // ----------------------------------------------------

        activityIdElement.textContent =
            assignment.assignment_id ||
            "Not detected";


        // ----------------------------------------------------
        // COURSE ID
        // ----------------------------------------------------

        courseIdElement.textContent =
            assignment.course_id ||
            "Not detected";


        // ----------------------------------------------------
        // PUBLISH STATUS
        // ----------------------------------------------------

        publishStatusElement.classList.remove(
            "published",
            "unpublished"
        );

        if (assignment.published === true) {
            publishStatusElement.textContent =
                "✓ Published";

            publishStatusElement.classList.add(
                "published"
            );

        } else if (
            assignment.published === false
        ) {
            publishStatusElement.textContent =
                "Unpublished";

            publishStatusElement.classList.add(
                "unpublished"
            );

        } else {
            publishStatusElement.textContent =
                "Status unknown";
        }


        // ----------------------------------------------------
        // SUBMISSION METHODS
        // ----------------------------------------------------

        const submission =
            formatSubmissionTypes(
                assignment.submission_types
            );

        submissionLabel.textContent =
            submission.label;

        submissionTypeElement.textContent =
            submission.value;


        // ----------------------------------------------------
        // DUE DATE
        // ----------------------------------------------------

        const due =
            formatCanvasDate(
                assignment.due_at
            );

        dueDateElement.textContent =
            due.date;

        dueTimeElement.textContent =
            due.time;


        // ----------------------------------------------------
        // TECHNICAL DETAILS
        // ----------------------------------------------------

        unlockDateElement.textContent =
            formatTechnicalDate(
                assignment.unlock_at
            );

        lockDateElement.textContent =
            formatTechnicalDate(
                assignment.lock_at
            );


        const usesExternalTool =
            Array.isArray(
                assignment.submission_types
            ) &&
            assignment.submission_types.includes(
                "external_tool"
            );

        if (usesExternalTool) {
            externalToolElement.textContent =
                assignment.external_tool
                    ? "Yes — details available"
                    : "Yes — details not available";

        } else {
            externalToolElement.textContent =
                "No";
        }


        // ----------------------------------------------------
        // SHOW TROUBLESHOOTING UI
        // ----------------------------------------------------

        statusElement.textContent =
            "Ready to troubleshoot.";

        troubleshootButton.style.display =
            "none";

        problemSection.style.display =
            "block";

    } catch (error) {
        console.error(
            "Assignment collection failed:",
            error
        );

        statusElement.textContent =
            "Could not collect assignment configuration.";

        troubleshootButton.textContent =
            "Try Again";

        troubleshootButton.disabled =
            false;
    }
}


// ------------------------------------------------------------
// DISPLAY DETERMINISTIC FINDINGS
// ------------------------------------------------------------

function displayTroubleshootingResult(result) {
    resultsContent.innerHTML = "";

    const aiData =
        result.ai_response &&
        result.ai_response.response
            ? result.ai_response.response
            : null;


    // --------------------------------------------------------
    // CREATEAI STRUCTURED RESPONSE
    // --------------------------------------------------------

    if (
        aiData &&
        typeof aiData === "object"
    ) {

        // HEADLINE

        if (aiData.headline) {
            const headline =
                document.createElement("div");

            headline.className =
                "result-title";

            headline.textContent =
                aiData.headline;

            headline.style.fontSize =
                "15px";

            headline.style.marginBottom =
                "8px";

            resultsContent.appendChild(
                headline
            );
        }


        // ANSWER

        if (aiData.answer) {
            const answer =
                document.createElement("div");

            answer.className =
                "result-recommendation";

            answer.textContent =
                aiData.answer;

            answer.style.fontSize =
                "13px";

            answer.style.lineHeight =
                "1.6";

            resultsContent.appendChild(
                answer
            );
        }


        // STEPS

        if (
            Array.isArray(aiData.steps) &&
            aiData.steps.length > 0
        ) {
            const label =
                document.createElement("div");

            label.className =
                "section-label";

            label.textContent =
                aiData.response_type ===
                "confirmed_issue"
                    ? "Recommended Action"
                    : "Next Steps";

            resultsContent.appendChild(
                label
            );


            const list =
                document.createElement("ol");

            list.style.paddingLeft =
                "20px";

            list.style.margin =
                "8px 0";

            aiData.steps.forEach(
                (step) => {
                    const item =
                        document.createElement(
                            "li"
                        );

                    item.textContent =
                        step;

                    item.style.fontSize =
                        "12px";

                    item.style.lineHeight =
                        "1.55";

                    item.style.marginBottom =
                        "5px";

                    list.appendChild(
                        item
                    );
                }
            );

            resultsContent.appendChild(
                list
            );
        }


        // IMPORTANT

        if (aiData.important) {
            const label =
                document.createElement("div");

            label.className =
                "section-label";

            label.textContent =
                "Important";

            resultsContent.appendChild(
                label
            );


            const important =
                document.createElement("div");

            important.className =
                "result-recommendation";

            important.textContent =
                aiData.important;

            resultsContent.appendChild(
                important
            );
        }


        // VERIFIED FACTS

        if (
            Array.isArray(aiData.verified) &&
            aiData.verified.length > 0
        ) {
            const label =
                document.createElement("div");

            label.className =
                "section-label";

            label.textContent =
                "Verified";

            resultsContent.appendChild(
                label
            );


            aiData.verified.forEach(
                (fact) => {
                    const item =
                        document.createElement(
                            "div"
                        );

                    item.textContent =
                        `✓ ${fact}`;

                    item.style.fontSize =
                        "12px";

                    item.style.marginBottom =
                        "6px";

                    resultsContent.appendChild(
                        item
                    );
                }
            );
        }


        resultsSection.style.display =
            "block";

        return;
    }


    // --------------------------------------------------------
    // FALLBACK TO DETERMINISTIC FINDINGS
    // --------------------------------------------------------

    const findings =
        result.findings || [];


    if (findings.length === 0) {
        const message =
            document.createElement("div");

        message.className =
            "result-recommendation";

        message.textContent =
            "No confirmed issue was identified by the available checks.";

        resultsContent.appendChild(
            message
        );

    } else {

        findings.forEach(
            (finding) => {

                const block =
                    document.createElement(
                        "div"
                    );

                block.className =
                    "result-item";


                const title =
                    document.createElement(
                        "div"
                    );

                title.className =
                    "result-title";

                title.textContent =
                    finding.issue ||
                    "Troubleshooting finding";


                const recommendation =
                    document.createElement(
                        "div"
                    );

                recommendation.className =
                    "result-recommendation";

                recommendation.textContent =
                    finding.recommendation ||
                    "No recommendation available.";


                block.appendChild(
                    title
                );

                block.appendChild(
                    recommendation
                );

                resultsContent.appendChild(
                    block
                );
            }
        );
    }


    resultsSection.style.display =
        "block";
}


// ------------------------------------------------------------
// ANALYZE PROBLEM
// ------------------------------------------------------------

async function analyzeProblem() {
    const problem =
        problemInput.value.trim();

    if (!problem) {
        statusElement.textContent =
            "Describe what students are experiencing first.";

        problemInput.focus();

        return;
    }

    if (!collectedAssignment) {
        statusElement.textContent =
            "Canvas configuration has not been collected.";

        return;
    }

        analyzeButton.disabled =
            true;

        analyzeButton.textContent =
            "Diagnosing...";

        statusElement.textContent =
            "Running troubleshooting checks...";

        resultsSection.style.display =
            "block";

    resultsContent.innerHTML = "";

    const loadingTitle =
        document.createElement("div");

    loadingTitle.className =
        "result-title";

    loadingTitle.textContent =
        "Analyzing Canvas evidence...";


    const loadingText =
        document.createElement("div");

    loadingText.className =
        "result-recommendation";

    loadingText.textContent =
        "Checking the available Canvas configuration and preparing guidance.";


    resultsContent.appendChild(
        loadingTitle
    );

    resultsContent.appendChild(
        loadingText
    );


    resultsSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });

    try {
        const response =
            await fetch(
                `${API_BASE_URL}/troubleshoot`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        problem: problem,
                        assignment:
                            collectedAssignment
                    })
                }
            );


        if (!response.ok) {
            throw new Error(
                `Troubleshooting service returned ${response.status}.`
            );
        }


        const result =
            await response.json();


        console.log(
            "Troubleshooting result:",
            result
        );


        displayTroubleshootingResult(
            result
        );
        resultsSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
        });
       
        analyzeButton.textContent =
            "Ask Another Question";

        statusElement.textContent =
            "Troubleshooting complete.";


    } catch (error) {
        console.error(
            "Troubleshooting failed:",
            error
        );

        statusElement.textContent =
            "Unable to complete troubleshooting. Check that the troubleshooting service is running.";

    } finally {
        analyzeButton.disabled =
            false;

    }
}


// ------------------------------------------------------------
// EVENTS
// ------------------------------------------------------------

troubleshootButton.addEventListener(
    "click",
    collectAssignmentData
);

analyzeButton.addEventListener(
    "click",
    analyzeProblem
);

async function checkBackendHealth() {
    try {
        const response = await fetch(
            `${API_BASE_URL}/health`
        );

        if (!response.ok) {
            return false;
        }

        const data = await response.json();

        return data.status === "ok";

    } catch (error) {
        console.error(
            "Backend health check failed:",
            error
        );

        return false;
    }
}

// ------------------------------------------------------------
// START
// ------------------------------------------------------------

detectCurrentPage();