const statusElement = document.getElementById("status");
const pageTypeElement = document.getElementById("pageType");
const courseIdElement = document.getElementById("courseId");
const activityIdElement = document.getElementById("activityId");
const activityNameElement = document.getElementById("activityName");
const troubleshootButton =
    document.getElementById("troubleshootButton");

const configurationSection =
    document.getElementById("configurationSection");

const problemSection =
    document.getElementById("problemSection");

const publishedElement =
    document.getElementById("published");

const submissionTypeElement =
    document.getElementById("submissionType");

const dueDateElement =
    document.getElementById("dueDate");

const unlockDateElement =
    document.getElementById("unlockDate");

const lockDateElement =
    document.getElementById("lockDate");

const externalToolElement =
    document.getElementById("externalTool");

const problemInput =
    document.getElementById("problemInput");

const analyzeButton =
    document.getElementById("analyzeButton");

const resultsSection =
    document.getElementById("resultsSection");

const resultsContent =
    document.getElementById("resultsContent");

let collectedAssignment = null;

async function getActiveTab() {
    const tabs = await chrome.tabs.query({
        active: true,
        currentWindow: true
    });

    if (!tabs.length) {
        throw new Error("No active browser tab found.");
    }

    return tabs[0];
}

async function ensureContentScript(tabId) {
    try {
        const response = await chrome.tabs.sendMessage(
            tabId,
            {
                type: "PING"
            }
        );

        if (response && response.ready) {
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


async function detectCurrentPage() {
    troubleshootButton.disabled = true;

    statusElement.textContent =
        "Checking current page...";

    try {
        const tab = await getActiveTab();

        await ensureContentScript(tab.id);

        const response = await chrome.tabs.sendMessage(
            tab.id,
            {
                type: "GET_CANVAS_CONTEXT"
            }
        );

        if (!response || !response.isCanvasPage) {
            statusElement.textContent =
                "This does not appear to be a Canvas course page.";

            return;
        }

        statusElement.textContent =
            "Canvas context detected.";

        pageTypeElement.textContent =
            response.pageType || "Unknown";

        courseIdElement.textContent =
            response.courseId || "Not detected";

        activityIdElement.textContent =
            response.activityId || "Not detected";

        activityNameElement.textContent =
            response.activityName || "Not detected";

        if (
            response.pageType === "Assignment" &&
            response.courseId &&
            response.activityId
        ) {
            troubleshootButton.disabled = false;
        } else {
            statusElement.textContent =
                "Canvas detected. Assignment troubleshooting is currently supported.";

            troubleshootButton.disabled = true;
        }

    } catch (error) {
        console.error(error);

        statusElement.textContent =
            "Unable to read this page.";

        troubleshootButton.disabled = true;
    }
}


async function collectAssignmentData() {
    troubleshootButton.disabled = true;

    troubleshootButton.textContent =
        "Collecting Canvas Data...";

    statusElement.textContent =
        "Reading assignment configuration...";

    try {
        const tab = await getActiveTab();


        await ensureContentScript(tab.id);

        const response = await chrome.tabs.sendMessage(
            tab.id,
            {
                type: "GET_ASSIGNMENT_DATA"
            }
        );

        if (!response || response.success !== true) {
            throw new Error(
                response?.error ||
                "Assignment data could not be collected."
            );
        }

    const assignment = response.assignment;

    collectedAssignment = assignment;

    console.log(
        "Canvas assignment data:",
        assignment
    );

    publishedElement.textContent = 
        assignment.published == true
        ? "Yes"
        :assignment.published == false
        ? "No"
        : "Unknown";

    
    if (
        Array.isArray(assignment.submission_types) &&
        assignment.submission_types.length > 0
    ) {
        submissionTypeElement.textContent = 
            assignment.submission_types
                .map((value) =>
                      value 
                          .replaceAll("_", " ")
                          .replace(
                            /\b\w/g,
                            (letter) =>
                                 letter.toUpperCase()
                          )
                )
                .join(", ");
    }else{
        submissionTypeElement.textContent =
            "Not set";
    }

    dueDateElement.textContent =
        assignment.due_at || "Not set";
    
    unlockDateElement.textContent =
        assignment.unlock_at || "Not set";
    
    lockDateElement.textContent =
        assignment.lock_at || "Not set";
    
    const usesExternalTool =
        Array.isArray(assignment.submission_types) &&
        assignment.submission_types.includes("external_tool");

    if (usesExternalTool) {
        externalToolElement.textContent =
            assignment.external_tool
                ? "Yes — details available"
                : "Yes — details not available";
    } else {
        externalToolElement.textContent ="No";
    }

    configurationSection.style.display =
        "block";

    problemSection.style.display =
        "block";

    statusElement.textContent =
        "Assignment configuration collected.";

    statusElement.classList.add(
        "success"
    );

    troubleshootButton.style.display =
        "none";

    } catch (error) {
        console.error(error);

        statusElement.textContent =
            "Could not collect assignment data: " +
            error.message;

        troubleshootButton.textContent =
            "Try Again";

        troubleshootButton.disabled = false;
    }
}

    troubleshootButton.addEventListener(
        "click",
        collectAssignmentData
    );

    function displayTroubleshootingResult(result) {
    resultsContent.innerHTML = "";

    const findings = result.findings || [];

    if (findings.length === 0) {
        const message =
            document.createElement("p");

        message.textContent =
            "No confirmed issue was identified by the available checks.";

        resultsContent.appendChild(message);

    } else {
        findings.forEach((finding) => {

            const findingBlock =
                document.createElement("div");

            findingBlock.style.marginBottom =
                "16px";

            const issue =
                document.createElement("strong");

            issue.textContent =
                finding.issue ||
                "Troubleshooting finding";

            const severity =
                document.createElement("div");

            severity.textContent =
                "Severity: " +
                (
                    finding.severity ||
                    "Not specified"
                );

            severity.style.marginTop =
                "5px";

            severity.style.fontSize =
                "12px";

            severity.style.color =
                "#64748b";

            const recommendation =
                document.createElement("p");

            recommendation.textContent =
                finding.recommendation ||
                "No recommendation available.";

            recommendation.style.fontSize =
                "13px";

            recommendation.style.lineHeight =
                "1.45";

            findingBlock.appendChild(issue);
            findingBlock.appendChild(severity);
            findingBlock.appendChild(
                recommendation
            );

            resultsContent.appendChild(
                findingBlock
            );
        });
    }

    resultsSection.style.display =
        "block";
}
    analyzeButton.addEventListener(
    "click",
    async () => {

        const problem =
            problemInput.value.trim();

        if (!problem) {
            statusElement.textContent =
                "Describe the problem before analyzing.";

            return;
        }

        if (!collectedAssignment) {
            statusElement.textContent =
                "Collect the Canvas configuration first.";

            return;
        }

        analyzeButton.disabled = true;
        analyzeButton.textContent =
            "Analyzing...";

        statusElement.textContent =
            "Running troubleshooting checks...";

        try {
            const response = await fetch(
                "http://127.0.0.1:8000/troubleshoot",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        problem: problem,
                        assignment: collectedAssignment
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

            statusElement.textContent =
                "Troubleshooting complete.";

            displayTroubleshootingResult(
                result
            );

        } catch (error) {
            console.error(error);

            statusElement.textContent =
                "Could not run troubleshooting: " +
                error.message;

        } finally {
            analyzeButton.disabled = false;

            analyzeButton.textContent =
                "Analyze Problem";
        }
    }
);
detectCurrentPage();