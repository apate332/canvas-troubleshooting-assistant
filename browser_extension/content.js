function detectCanvasContext() {
    const url = new URL(window.location.href);
    const pathParts = url.pathname
        .split("/")
        .filter(Boolean);

    const context = {
        isCanvasPage: false,
        pageType: null,
        courseId: null,
        activityId: null,
        moduleItemId: null,
        activityName: null,
        url: window.location.href
    };
    
    context.moduleItemId =
    url.searchParams.get("module_item_id");
    

    const coursesIndex = pathParts.indexOf("courses");

    if (
        coursesIndex === -1 ||
        !pathParts[coursesIndex + 1]
    ) {
        return context;
    }

    context.isCanvasPage = true;
    context.courseId = pathParts[coursesIndex + 1];

    const assignmentsIndex =
        pathParts.indexOf("assignments");

    const modulesIndex =
        pathParts.indexOf("modules");

    const quizzesIndex =
        pathParts.indexOf("quizzes");

    if (
        assignmentsIndex !== -1 &&
        pathParts[assignmentsIndex + 1]
    ) {
        context.pageType = "Assignment";
        context.activityId =
            pathParts[assignmentsIndex + 1];

    } else if (
        quizzesIndex !== -1 &&
        pathParts[quizzesIndex + 1]
    ) {
        context.pageType = "Quiz";
        context.activityId =
            pathParts[quizzesIndex + 1];

    } else if (modulesIndex !== -1) {
        context.pageType = "Module";

        if (pathParts[modulesIndex + 1]) {
            context.activityId =
                pathParts[modulesIndex + 1];
        }

    } else {
        context.pageType = "Course";
    }

    const heading =
        document.querySelector("h1") ||
        document.querySelector(
            '[data-testid="assignment-name"]'
        );

    if (heading) {
        context.activityName =
            heading.textContent.trim();
    } else {
        context.activityName =
            document.title
                .replace(/\s*:\s*Canvas\s*$/i, "")
                .trim();
    }

    return context;
}

async function getAssignmentData(context) {
    if (
        context.pageType !== "Assignment" ||
        !context.courseId ||
        !context.activityId
    ) {
        throw new Error(
            "The current page is not a supported assignment page."
        );
    }

    const endpoint =
        `/api/v1/courses/${context.courseId}` +
        `/assignments/${context.activityId}`;

    const response = await fetch(endpoint, {
        method: "GET",
        credentials: "same-origin",
        headers: {
            "Accept": "application/json"
        }
    });

    if (!response.ok) {
        throw new Error(
            `Canvas returned ${response.status}.`
        );
    }

    const assignment = await response.json();

    return {
        assignment_id: assignment.id,
        course_id: assignment.course_id,
        name: assignment.name,

        published:
            assignment.published ??
            (assignment.workflow_state === "published"),

        workflow_state:
            assignment.workflow_state,

        due_at:
            assignment.due_at,

        unlock_at:
            assignment.unlock_at,

        lock_at:
            assignment.lock_at,

        submission_types:
            assignment.submission_types,

        points_possible:
            assignment.points_possible,

        grading_type:
            assignment.grading_type,

        allowed_attempts:
            assignment.allowed_attempts,

        assignment_group_id:
            assignment.assignment_group_id,

        external_tool:
            assignment.external_tool_tag_attributes
                ? {
                    url:
                        assignment
                            .external_tool_tag_attributes
                            .url,

                    resource_link_id:
                        assignment
                            .external_tool_tag_attributes
                            .resource_link_id,

                    content_type:
                        assignment
                            .external_tool_tag_attributes
                            .content_type
                }
                : null
    };
}

chrome.runtime.onMessage.addListener(
    (message, sender, sendResponse) => {

        if (message.type === "GET_CANVAS_CONTEXT") {
            sendResponse(
                detectCanvasContext()
            );

            return true;
        }

        if (message.type === "GET_ASSIGNMENT_DATA") {

            const context =
                detectCanvasContext();

            getAssignmentData(context)
                .then((assignment) => {
                    sendResponse({
                        success: true,
                        assignment: assignment
                    });
                })
                .catch((error) => {
                    sendResponse({
                        success: false,
                        error: error.message
                    });
                });

            return true;
        }
    }
);